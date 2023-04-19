"""
MOl V3000 format
"""
import math
import os
from typing import List

from structurefinder.db.mapping import Atoms
from structurefinder.shelxfile.elements import get_radius_from_element


class MolFile(object):
    """
    This mol file writer is only to use the file with JSmol, not to implement the standard exactly!
    """

    def __init__(self, atoms: List[Atoms], bonds = None):
        self.atoms = atoms
        if bonds:
            self.bonds = bonds
        else:
            self.bonds = self.get_conntable_from_atoms()
        self.bondscount = len(self.bonds)
        self.atomscount = len(self.atoms)

    def header(self) -> str:
        """
        For JSmol, I don't need a facy header.
        """
        return f"{os.linesep}{os.linesep}{os.linesep}"

    def connection_table(self) -> str:
        """
          6  6  0  0  0  0  0  0  0  0  1 V3000
        """
        tab = f"{self.atomscount:>5d}{self.bondscount:>5d}"
        return tab

    def get_atoms_string(self) -> str:
        """
        Returns a string with an atom in each line.
        X Y Z Element
        """
        atoms = []
        for at in self.atoms:
            atoms.append(f"{at.xc:>10.4f}{at.yc:>10.4f}{at.zc:>10.4f} {at.element:<2s}")
        return '\n'.join(atoms)

    def get_bonds_string(self) -> str:
        """
        This is not accodingly to the file standard!
        The standard wants to have fixed format 3 digits for the bonds.
        """
        blist = []
        for bo in self.bonds:
            # This is deviating from the standard:
            blist.append(f"{bo[0]:>4d}{bo[1]:>4d}  1  0  0  0  0")
        return '\n'.join(blist)

    def get_conntable_from_atoms(self, extra_param=0.48):
        """
        returns a connectivity table from the atomic coordinates and the covalence
        radii of the atoms.
        a bond is defined with less than the sum of the covalence radii plus the extra_param:
        :param extra_param: additional distance to the covalence radius
        :type extra_param: float
        """
        #t1 = perf_counter()
        conlist = []
        for num1, at1 in enumerate(self.atoms, 1):
            at1_part = at1.part
            rad1 = get_radius_from_element(at1.element)
            for num2, at2 in enumerate(self.atoms, 1):
                at2_part = at2.part
                if at1_part * at2_part != 0 and at1_part != at2_part:
                    continue
                if at1.Name == at2.Name:  # name1 = name2
                    continue
                d = math.dist((at1.xc, at1.yc, at1.zc), (at2.xc, at2.yc, at2.zc))
                if d > 4.0:  # makes bonding faster (longer bonds do not exist)
                    continue
                rad2 = get_radius_from_element(at2.element)
                if (rad1 + rad2) + extra_param > d:
                    if at1.element == 'H' and at2.element == 'H':
                        continue
                    # print(num1, num2, d)
                    # The extra time for this is not too much:
                    if [num2, num1] in conlist:
                        continue
                    conlist.append([num1, num2])
        #t2 = perf_counter()
        #print('Bondzeit:', round(t2-t1, 3), 's')
        #print('len:', len(conlist))
        return conlist

    def footer(self) -> str:
        """
        """
        return f"M  END{os.linesep}$$$$"

    def make_mol(self):
        """
        Combines all above to a mol file.
        """
        header = '\n\n'
        connection_table = self.connection_table()
        atoms = self.get_atoms_string()
        bonds = self.get_bonds_string()
        footer = self.footer()
        mol = "{0}{5}{1}{5}{2}{5}{3}{5}{4}".format(header, connection_table, atoms, bonds, footer, '\n')
        return mol
