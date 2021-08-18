# -*- encoding: utf-8 -*-
# möp
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <daniel.kratzert@ac.uni-freiburg.de> wrote this file. As long as you retain
# this notice you can do whatever you want with this stuff. If we meet some day,
# and you think this stuff is worth it, you can buy me a beer in return.
# Daniel Kratzert
# ----------------------------------------------------------------------------
#


import time
from math import sqrt, cos, radians, sin

from searcher import database_handler
from shelxfile.elements import get_radius_from_element
from shelxfile.dsrmath import Array, SymmetryElement, Matrix, frac_to_cart

DEBUG = False


class Atom():
    def __init__(self, name, element, x, z, y, part):
        self._dict = {'name': name, 'element': element, 'x': x, 'y': y, 'z': z,
                      'part': part, 'molindex': None}

    def __getitem__(self, key):
        return self._dict[key]

    def __repr__(self):
        return "Atom: " + repr(self._dict)

    def __setitem__(self, key, val):
        self._dict[key] = val

    def __iter__(self):
        return iter(['name', 'element', 'x', 'y', 'z', 'part', 'molindex'])


class SymmCards():
    """
    Contains the list of SYMM cards
    """

    def __init__(self):
        self._symmcards = []

    def _as_str(self) -> str:
        return "\n".join([str(x) for x in self._symmcards])

    def __repr__(self) -> str:
        return self._as_str()

    def __str__(self) -> str:
        return self._as_str()

    def __getitem__(self, item):
        return self._symmcards[item]

    def __iter__(self):
        for x in self._symmcards:
            yield x

    def append(self, symmData: list) -> None:
        """
        Add the content of a Shelxl SYMM command to generate the appropriate SymmetryElement instance.
        :param symmData: list of strings. eg.['1/2+X', '1/2+Y', '1/2+Z']
        :return: None
        """
        newSymm = SymmetryElement(symmData)
        self._symmcards.append(newSymm)


class SDMItem(object):
    __slots__ = ['dist', 'atom1', 'atom2', 'a1', 'a2', 'symmetry_number', 'covalent', 'dddd']

    def __init__(self):
        self.dist = 0.0
        self.atom1 = None
        self.a1 = 0
        self.atom2 = None
        self.a2 = 0
        self.symmetry_number = 0
        self.covalent = True
        self.dddd = 0

    def __lt__(self, a2):
        return True if self.dist < a2.dist else False

    def __eq__(self, other: 'SDMItem'):
        if other.a1 == self.a2 and other.a2 == self.a1:
            return True
        return False

    def __repr__(self):
        return '{} {} {} {} dist: {} coval: {} sn: {} {}'.format(self.atom1.name, self.atom2.name, self.a1, self.a2,
                                                                 self.dist, self.covalent,
                                                                 self.symmetry_number, self.dddd)


class SDM():
    def __init__(self, atoms: list, symmcards: list, cell: list):
        """
        Calculates the shortest distance matrix
                        0      1      2  3  4   5     6          7
        :param atoms: [Name, Element, X, Y, Z, Part, ocuupancy, molindex -> (later)]
        :param symmcards:
        :param cell:
        """
        self.atoms = atoms
        self.symmcards = SymmCards()
        for s in symmcards:
            self.symmcards.append(s)
        self.cell = cell
        self.cosal = cos(radians(cell[3]))
        self.cosbe = cos(radians(cell[4]))
        self.cosga = cos(radians(cell[5]))
        self.aga = self.cell[0] * self.cell[1] * self.cosga
        self.bbe = self.cell[0] * self.cell[2] * self.cosbe
        self.cal = self.cell[1] * self.cell[2] * self.cosal
        self.asq = self.cell[0] ** 2
        self.bsq = self.cell[1] ** 2
        self.csq = self.cell[2] ** 2
        self.sdm_list = []  # list of sdmitems
        self.maxmol = 1
        self.sdmtime = 0
        self.bondlist = []

    def orthogonal_matrix(self):
        """
        Converts von fractional to cartesian by .
        Invert the matrix to do the opposite.
        """
        return Matrix([[self.cell[0], self.cell[1] * cos(self.cell[5]), self.cell[2] * cos(self.cell[4])],
                       [0, self.cell[1] * sin(self.cell[5]),
                        (self.cell[2] * (cos(self.cell[3]) - cos(self.cell[4]) * cos(self.cell[5])) / sin(
                                self.cell[5]))],
                       [0, 0, self.cell[6] / (self.cell[0] * self.cell[1] * sin(self.cell[5]))]])

    def calc_sdm(self) -> list:
        t1 = time.perf_counter()
        self.bondlist.clear()
        for i, at1 in enumerate(self.atoms):
            prime_array = [Array(at1[2:5]) * symop.matrix + symop.trans for symop in self.symmcards]
            for j, at2 in enumerate(self.atoms):
                mind = 1000000
                hma = False
                at2_plushalf = Array(at2[2:5]) + 0.5
                sdmItem = SDMItem()
                for n, symop in enumerate(self.symmcards):
                    D = prime_array[n] - at2_plushalf
                    dp = [v - 0.5 for v in D - D.floor]
                    dk = self.vector_length(*dp)
                    if n:
                        dk += 0.0001
                    if dk > 4.0:
                        continue
                    if (dk > 0.01) and (mind >= dk):
                        mind = min(dk, mind)
                        sdmItem.dist = mind
                        sdmItem.atom1 = at1
                        sdmItem.atom2 = at2
                        sdmItem.a1 = i
                        sdmItem.a2 = j
                        sdmItem.symmetry_number = n
                        hma = True
                if not sdmItem.atom1:
                    # Do not grow grown atoms:
                    continue
                if (not sdmItem.atom1[1] in ['H', 'D'] and not sdmItem.atom2[1] in ['H', 'D']) and \
                        sdmItem.atom1[5] * sdmItem.atom2[5] == 0 or sdmItem.atom1[5] == sdmItem.atom2[5]:
                    dddd = (get_radius_from_element(at1[1]) + get_radius_from_element(at2[1])) * 1.2
                    sdmItem.dddd = dddd
                else:
                    dddd = 0.0
                if sdmItem.dist < dddd:
                    if hma:
                        sdmItem.covalent = True
                        # self.bondlist.append((i, j, sdmItem.atom1[0], sdmItem.atom2[0], sdmItem.dist))
                else:
                    sdmItem.covalent = False
                if hma:
                    self.sdm_list.append(sdmItem)
        t2 = time.perf_counter()
        self.sdmtime = t2 - t1
        # if DEBUG:
        print('Time for sdm:', round(self.sdmtime, 3), 's')
        self.sdm_list.sort()
        self.calc_molindex(self.atoms)
        need_symm = self.collect_needed_symmetry()
        if DEBUG:
            print("The asymmetric unit contains {} fragments.".format(self.maxmol))
        return need_symm

    def collect_needed_symmetry(self) -> list:
        need_symm = []
        # Collect needsymm list:
        for sdmItem in self.sdm_list:
            if sdmItem.covalent:
                if sdmItem.atom1[-1] < 1 or sdmItem.atom1[-1] > 6:
                    continue
                for n, symop in enumerate(self.symmcards):
                    if sdmItem.atom1[5] != 0 and sdmItem.atom2[5] != 0 \
                            and sdmItem.atom1[5] != sdmItem.atom2[5]:
                        # both not part 0 and different part numbers
                        continue
                    # Both the same atomic number and number 0 (hydrogen)
                    if sdmItem.atom1[1] == sdmItem.atom2[1] and sdmItem.atom1[1] in ['H', 'D']:
                        continue
                    prime = Array(sdmItem.atom1[2:5]) * symop.matrix + symop.trans
                    D = prime - Array(sdmItem.atom2[2:5]) + Array([0.5, 0.5, 0.5])
                    floorD = D.floor
                    dp = D - floorD - Array([0.5, 0.5, 0.5])
                    if n == 0 and Array([0, 0, 0]) == floorD:
                        continue
                    dk = self.vector_length(*dp)
                    dddd = sdmItem.dist + 0.2
                    # Idea for fast bon list:
                    # self.bondlist.append((sdmItem.a1, sdmItem.a2, sdmItem.atom1[0] + '<',
                    #                      sdmItem.atom2[0] + '<', sdmItem.dist))
                    if sdmItem.atom1[1] in ['H', 'D'] and sdmItem.atom2[1] in ['H', 'D']:
                        dddd = 1.8
                    if (dk > 0.001) and (dddd >= dk):
                        bs = [n + 1, (5 - floorD[0]), (5 - floorD[1]), (5 - floorD[2]), sdmItem.atom1[-1]]
                        if bs not in need_symm:
                            need_symm.append(bs)
        return need_symm

    def calc_molindex(self, all_atoms):
        # Start for George's "bring atoms together algorithm":
        someleft = 1
        nextmol = 1
        for at in all_atoms:
            at.append(-1)
        all_atoms[0][-1] = 1
        while nextmol:
            someleft = 1
            nextmol = 0
            while someleft:
                someleft = 0
                for sdmItem in self.sdm_list:
                    if sdmItem.covalent and sdmItem.atom1[-1] * sdmItem.atom2[-1] < 0:
                        sdmItem.atom1[-1] = self.maxmol  # last item is the molindex
                        sdmItem.atom2[-1] = self.maxmol
                        someleft += 1
            for ni, at in enumerate(all_atoms):
                if at[-1] < 0:
                    nextmol = ni
                    break
            if nextmol:
                self.maxmol += 1
                all_atoms[nextmol][-1] = self.maxmol

    def vector_length(self, x: float, y: float, z: float) -> float:
        """
        Calculates the vector length given in fractional coordinates.
        """
        A = 2.0 * (x * y * self.aga + x * z * self.bbe + y * z * self.cal)
        return sqrt(x ** 2 * self.asq + y ** 2 * self.bsq + z ** 2 * self.csq + A)

    def packer(self, sdm: 'SDM', need_symm: list, with_qpeaks=False):
        """
        Packs atoms of the asymmetric unit to real molecules.
        """
        showatoms = self.atoms[:]
        new_atoms = []
        for symm in need_symm:
            s, h, k, l, symmgroup = symm
            h -= 5
            k -= 5
            l -= 5
            s -= 1
            for atom in self.atoms:
                if atom[-1] == symmgroup:
                    coords = Array(atom[2:5]) * self.symmcards[s].matrix \
                             + Array(self.symmcards[s].trans) + Array([h, k, l])
                    # The new atom:
                    new = [atom[0], atom[1]] + list(coords) + [atom[5], atom[6], atom[7], 'symmgen']
                    new_atoms.append(new)
                    isthere = False
                    # Only add atom if its occupancy (new[5]) is greater zero:
                    if new[5] >= 0:
                        for atom in showatoms:
                            if atom[5] != new[5]:
                                continue
                            length = sdm.vector_length(new[2] - atom[2],
                                                       new[3] - atom[3],
                                                       new[4] - atom[4])
                            if length < 0.2:
                                isthere = True
                    if not isthere:
                        showatoms.append(new)
                # elif grow_qpeaks:
                #    add q-peaks here
        cart_atoms = []
        for a in showatoms:
            cart_atoms.append(self.to_cartesian(a))
        return cart_atoms

    def to_cartesian(self, at):
        return list(at[:2]) + frac_to_cart([at[2], at[3], at[4]], self.cell[:6]) + list(at[5:])


if __name__ == "__main__":
    structureId = 7
    structures = database_handler.StructureTable('./test.sqlite')
    cell = structures.get_cell_by_id(structureId)
    atoms = structures.get_atoms_table(structureId, cartesian=False, as_list=True)
    symmcards = [x.split(',') for x in structures.get_row_as_dict(structureId)['_space_group_symop_operation_xyz'] \
        .replace("'", "").replace(" ", "").split("\n")]
    sdm = SDM(atoms, symmcards, cell)
    needsymm = sdm.calc_sdm()
    # print(needsymm)
    # sys.exit()
    packed_atoms = sdm.packer(sdm, needsymm)
    # print(needsymm)
    # [[8, 5, 5, 5, 1], [16, 5, 5, 5, 1], [7, 4, 5, 5, 3]]
    # print(len(shx.atoms))
    # print(len(packed_atoms))

    # for at in packed_atoms:
    #    print(at)

    print('Zeit für sdm:', round(sdm.sdmtime, 3), 's')
