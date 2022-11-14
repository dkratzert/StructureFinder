

from math import acos, sqrt, degrees

from structurefinder.shelxfile import elements
from structurefinder.shelxfile.cards import AFIX, PART, RESI
from structurefinder.shelxfile.dsrmath import atomic_distance, frac_to_cart, Array
from structurefinder.shelxfile.misc import DEBUG, split_fvar_and_parameter, ParseUnknownParam, ParseSyntaxError

"""
TODO:

"""


class Atoms():
    """
    All atoms from a SHELXL file with their properties.
    """

    def __init__(self, shx):
        self.shx = shx
        self.all_atoms = []

    def append(self, atom: 'Atom') -> None:
        """
        Adds a new atom to the list of atoms. Using append is essential.
        """
        self.all_atoms.append(atom)

    @property
    def nameslist(self):
        return [at.fullname.upper() for at in self.all_atoms]

    def __repr__(self):
        if self.all_atoms:
            return '\n'.join([str(x) for x in self.all_atoms])
        else:
            return 'No Atoms in file.'

    def __iter__(self):
        return iter(x for x in self.all_atoms)

    def __getitem__(self, item: int) -> 'Atom':
        return self.get_atom_by_id(item)

    def __len__(self) -> int:
        return len(self.all_atoms)

    def __delitem__(self, key):
        """
        Delete an atom by its atomid:
        del atoms[4]
        """
        for n, at in enumerate(self.all_atoms):
            if key == at.atomid:
                if DEBUG:
                    print("deleting atom", at.fullname)
                del self.all_atoms[n]
                del self.shx._reslist[self.shx._reslist.index(at)]
        # if DEBUG:
        #    print('Could not delete atom {}'.format(self.get_atom_by_id(key.atomid).fullname))

    @property
    def atomsdict(self):
        return dict((atom.fullname, atom) for atom in self.all_atoms)

    @property
    def number(self) -> int:
        """
        The number of atoms in the current SHELX file.
        >>> from structurefinder import ShelXFile
        >>> shx = ShelXFile('./test-data/p21c.res')
        >>> shx.atoms.number
        148
        """
        return len(self.all_atoms)

    def get_atom_by_id(self, aid: int) -> 'Atom':
        """
        Returns the atom objext with atomId id.
        """
        for a in self.all_atoms:
            if aid == a.atomid:
                return a

    def has_atom(self, atom_name: str) -> bool:
        """
        Returns true if shelx file has atom.

        >>> from structurefinder import ShelXFile
        >>> shx = ShelXFile('./test-data/p21c.res')
        >>> shx.atoms.has_atom('Al1')
        True
        >>> shx.atoms.has_atom('Al1_0')
        True
        >>> shx.atoms.has_atom('Al2_0')
        False
        """
        if '_' not in atom_name:
            atom_name += '_0'
        if atom_name.upper() in self.nameslist:
            return True
        else:
            return False

    def get_atom_by_name(self, atom_name: str) -> 'Atom' or None:
        """
        Returns an Atom object using an atom name with residue number like C1, C1_0, F2_4, etc.
        C1 means atom C1 in residue 0.
        >>> from structurefinder import ShelXFile
        >>> shx = ShelXFile('./test-data/p21c.res')
        >>> shx.atoms.get_atom_by_name('Al1')
        Atom ID: 73
        """
        if '_' not in atom_name:
            if atom_name == ">" or atom_name == "<":
                return None
            atom_name += '_0'
        try:
            at = self.atomsdict[atom_name.upper()]
        except KeyError:
            print("Atom {} not found in atom list.".format(atom_name))
            return None
        return at

    def get_multi_atnames(self, atom_name, residue_class):
        atoms = []
        if residue_class:
            for num in self.shx.residues.residue_classes[residue_class]:
                if '_' not in atom_name:
                    atom_name += '_0'
                else:
                    atom_name += '_{}'.format(num)
                try:
                    atoms.append(self.atomsdict[atom_name.upper()])
                except KeyError:
                    pass
        else:
            try:
                atoms.append(self.atomsdict[atom_name.upper()])
            except KeyError:
                return None
        return atoms

    def get_all_atomcoordinates(self) -> dict:
        """
        Returns a dictionary {'C1': ['1.123', '0.7456', '3.245'], 'C2_2': ...}
        >>> from structurefinder import ShelXFile
        >>> shx = ShelXFile('./test-data/p21c.res')
        >>> shx.atoms.get_all_atomcoordinates() # doctest: +ELLIPSIS
        {'O1_4': [0.074835, 0.238436, 0.402457], 'C1_4': [0.028576, 0.234542, 0.337234], ...}
        """
        atdict = {}
        for at in self.all_atoms:
            # if at.qpeak:
            #    atdict[at.name] = at.frac_coords
            # else:
            atdict[at.name.upper() + '_' + str(at.resinum)] = at.frac_coords
        return atdict

    def get_frag_fend_atoms(self) -> list:
        """
        Returns a list of atoms with cartesian coordinates. Atom names and sfac are ignored. They come from AFIX 17x.
        [[0.5316439256202359, 7.037351406500001, 10.112963255220803],
        [-1.7511017452002604, 5.461541059000001, 10.01187984858907]]
        """
        atoms = []
        for at in self.all_atoms:
            if at.frag_atom:
                atoms.append([at.xc, at.yc, at.zc])
        return atoms

    @property
    def residues(self) -> list:
        """
        Returns a list of the residue numbers in the shelx file.
        >>> from structurefinder import ShelXFile
        >>> shx = ShelXFile('./test-data/p21c.res')
        >>> shx.atoms.residues
        [0, 1, 2, 3, 4]
        """
        return list(set([x.resinum for x in self.all_atoms]))

    @property
    def q_peaks(self) -> list:
        r"""
        Returns a list of q-peaks in the file.
        >>> from structurefinder import ShelXFile
        >>> shx = ShelXFile('./test-data/p21c.res')
        >>> shx.atoms.q_peaks[:5] # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        [Atom ID: 328, Atom ID: 329, Atom ID: 330, Atom ID: 331, Atom ID: 332]
        """
        return [x for x in self.all_atoms if x.qpeak]

    def distance(self, atom1: str, atom2: str) -> float:
        """
        Calculates the (shortest) distance of two atoms given as text names e.g. C1_3.
        >>> from structurefinder import ShelXFile
        >>> shx = ShelXFile('./test-data/p21c.res')
        >>> round(shx.atoms.distance('F1_2', 'F2_2'), 6)
        2.154399
        >>> round(shx.atoms.distance('C2_2', 'F1_2'), 6)
        1.332854
        """
        a1 = self.get_atom_by_name(atom1)
        a2 = self.get_atom_by_name(atom2)
        try:
            return atomic_distance([a1.xc, a1.yc, a1.zc], [a2.xc, a2.yc, a2.zc])
        except AttributeError:
            return 0.0

    def angle(self, at1: 'Atom', at2: 'Atom', at3: 'Atom') -> float:
        """
        Calculates the angle between three atoms.

        >>> from structurefinder import ShelXFile
        >>> shx = ShelXFile('./test-data/p21c.res')
        >>> at1 = shx.atoms.get_atom_by_name('O1_4')
        >>> at2 = shx.atoms.get_atom_by_name('C1_4')
        >>> at3 = shx.atoms.get_atom_by_name('C2_4')
        >>> round(shx.atoms.angle(at1, at2, at3), 6)
        109.688123
        """
        ac1 = Array(at1.cart_coords)
        ac2 = Array(at2.cart_coords)
        ac3 = Array(at3.cart_coords)
        vec1 = ac2 - ac1
        vec2 = ac2 - ac3
        return vec1.angle(vec2)

    def torsion_angle(self, at1: 'Atom', at2: 'Atom', at3: 'Atom', at4: 'Atom') -> float:
        """
        Calculates the torsion angle (dieder angle) between four atoms.

        From the book of Camelo Giacovazzo:
        For a sequence of four atoms A, B, C, D, the torsion angle w(ABCD) is
        defined as the angle between the normals to the planes ABC and BCD.
        By convention w is positive if the sense of rotation from BA to
        CD, viewed down BC, is clockwise, otherwise it is negative.

        >>> from structurefinder import ShelXFile
        >>> shx = ShelXFile('./test-data/p21c.res')
        >>> at1 = shx.atoms.get_atom_by_name('O1')
        >>> at2 = shx.atoms.get_atom_by_name('C1')
        >>> at3 = shx.atoms.get_atom_by_name('C2')
        >>> at4 = shx.atoms.get_atom_by_name('F1')
        >>> round(shx.atoms.torsion_angle(at1, at2, at3, at4), 6)
        74.095731
        >>> at4 = shx.atoms.get_atom_by_name('F2')
        >>> round(shx.atoms.torsion_angle(at1, at2, at3, at4), 6)
        -44.467358
        """
        ac1 = Array(at1.cart_coords)
        ac2 = Array(at2.cart_coords)
        ac3 = Array(at3.cart_coords)
        ac4 = Array(at4.cart_coords)
        # Three vectors between four atoms:
        v1 = ac2 - ac1
        v2 = ac3 - ac2
        v3 = ac4 - ac3
        # cross product:
        a = v1.cross(v2)
        b = v2.cross(v3)
        # If direction > 0, angle is positive, else negative:
        direction = v1[0] * v2[1] * v3[2] - v1[2] * v1[1] * v3[0] + v1[2] * v2[0] * v3[1] - v1[0] \
                    * v2[2] * v3[1] + v1[1] * v2[2] * v3[0] - v1[1] * v2[0] * v3[2]
        # angle between plane normals:
        ang = acos((a[0] * b[0] + a[1] * b[1] + a[2] * b[2]) /
                   (sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2]) *
                    sqrt(b[0] * b[0] + b[1] * b[1] + b[2] * b[2])))
        return degrees(ang) if direction > 0 else degrees(-ang)

    def atoms_in_class(self, name: str) -> list:
        """
        Returns a list of atoms in residue class 'name'
        >>> from structurefinder import ShelXFile
        >>> shx = ShelXFile('./test-data/p21c.res')
        >>> shx.atoms.atoms_in_class('CCF3')
        ['O1', 'C1', 'C2', 'F1', 'F2', 'F3', 'C3', 'F4', 'F5', 'F6', 'C4', 'F7', 'F8', 'F9']
        """
        atoms = []
        for x in self.all_atoms:
            if x.resiclass == name:
                if x.name not in atoms:
                    atoms.append(x.name)
        return atoms


class Atom():
    """
    An object holding all Properties of a shelxl atom plus some extra information like
    kartesian coordinates and element type.
    """
    #                name    sfac     x         y        z       occ      u11      u12 ...
    _anisatomstr = '{:<4.4s}{:>3}{:>12.6f}{:>12.6f}{:>12.6f}{:>12.5f}{:>11.5f}=\n  {:>11.5f}' \
                   ' {:>12.5f}{:>11.5f}{:>11.5f}{:>11.5f}'  # Line wrap is handled during file write.
    #               name    sfac     x         y         z         occ      u11
    _isoatomstr = '{:<5.5s} {:<3}{:>10.6f}  {:>10.6f}  {:>9.6f}  {:>9.5f}  {:>9.5f}'
    _qpeakstr = '{:<5.5s} {:<3}{:>8.4f}  {:>8.4f}  {:>8.4f}  {:>9.5f}  {:<9.2f} {:<9.2f}'
    _fragatomstr = '{:<5.5s} {:>10.6f}  {:>10.6f}  {:>9.6f}'

    def __init__(self, shx) -> None:
        self.shx = shx
        self.cell = shx.cell
        self.sfac_num = None
        self.resi = None
        self.part = None
        self.afix = None
        self.name = 'name'  # Name without residue number like "C1"
        # Site occupation factor including free variable like 31.0
        self.sof = 11.0
        # fractional coordinates:
        self.x = None
        self.y = None
        self.z = None
        # cartesian coordinates:
        self.xc = None
        self.yc = None
        self.zc = None
        self.qpeak = False
        self.peak_height = 0.0
        self.uvals = [0.04]  # [U] or [u11 u12 u13 u21 u22 u23]
        self.uvals_orig = [0.04]
        self.frag_atom = False
        self.restraints = []
        self.previous_non_h = None  # Find in self.shx.atoms durinf initialization
        self._line_numbers = None
        self._occupancy = 1.0
        self.molindex = 0
        # Indicates if this atom is generated by symmetry:
        self.symmgen = False

    @property
    def atomid(self) -> int:
        if self.symmgen:
            return 0
        try:
            return self.shx._reslist.index(self)
        except ValueError:
            return 0

    @property
    def fullname(self) -> str:
        return self.name + '_' + str(self.resinum)  # Name including residue nimber like "C1_2"

    @property
    def resiclass(self) -> str:
        return self.resi.residue_class

    @property
    def resinum(self) -> int:
        return self.resi.residue_number

    @property
    def chain_id(self) -> str:
        return self.resi.chainID

    @property
    def fvar(self) -> int:
        # Be aware: fvar can be negative!
        fvar, _ = split_fvar_and_parameter(self.sof)
        return fvar

    @property
    def occupancy(self) -> float:
        # Only the occupancy of the atom like 0.5 (without the free variable)
        _, occ = split_fvar_and_parameter(self.sof)
        # Fractional occupancy:
        if abs(self.fvar) == 1:
            return occ
        else:
            if occ > 0:
                try:
                    occ = self.shx.fvars[self.fvar] * occ
                except IndexError:
                    occ = 1.0  # Happens if the self.fvar is not defined
                    if DEBUG:
                        raise ParseSyntaxError
            else:
                try:
                    occ = 1 + (self.shx.fvars[self.fvar] * occ)
                except IndexError:
                    occ = 1.0
                    if DEBUG:
                        raise ParseSyntaxError
        return occ

    @occupancy.setter
    def occupancy(self, occ: float):
        self._occupancy = occ

    @property
    def ishydrogen(self) -> bool:
        """
        Returns True if the current atom is a hydrogen isotope.
        """
        if self.element in ['H', 'D', 'T']:
            return True
        else:
            return False

    def set_atom_parameters(self, name: str = 'C', sfac_num: int = 1, coords: list = None, part: PART = None,
                            afix: AFIX = None, resi: RESI = None, site_occupation: float = 11.0, uvals: list = None,
                            symmgen: bool = True):
        """
        Sets atom properties manually if not parsed from a SHELXL file.
        """
        self.name = name
        self.sfac_num = sfac_num
        self.frac_coords = coords
        self.x, self.y, self.z = coords[0], coords[1], coords[2]
        self.xc, self.yc, self.zc = frac_to_cart(self.frac_coords, self.cell)
        self.part = part
        self.afix = afix
        self.resi = resi
        self.sof = site_occupation
        self.uvals = uvals
        self.symmgen = symmgen

    def set_uvals(self, uvals: list):
        """
        Sets u values and checks if a free variable was used.
        """
        self.uvals = uvals
        if len(uvals) != 2:  # two means Uiso anf q-peak hight
            for n, u in enumerate(uvals):
                if abs(u) > 4.0:
                    fvar, uval = split_fvar_and_parameter(u)
                    #self.uvals[n] = uval
                    self.shx.fvars.set_fvar_usage(fvar)
        else:
            if abs(uvals[0]) > 4.0:
                fvar, uval = split_fvar_and_parameter(uvals[0])
                self.shx.fvars.set_fvar_usage(fvar)

    def parse_line(self, atline: list, list_of_lines: list, part: PART, afix: AFIX, resi: RESI):
        """
        Parsers the text line of an atom from SHELXL to initialize the atom parameters.
        """
        self.name = atline[0][:4]  # Atom names are limited to 4 characters
        uvals = [float(x) for x in atline[6:12]]
        self.uvals_orig = uvals[:]
        self.set_uvals(uvals)
        self._line_numbers = list_of_lines
        self.part = part
        self.afix = afix
        self.resi = resi
        # TODO: test all variants of PART and AFIX sof combinations:
        if self.part.sof != 11.0:
            if self.afix and self.afix.sof:  # handles position of afix and part:
                if self.afix.index > self.part.index:
                    self.sof = self.afix.sof
            else:
                self.sof = self.part.sof
        elif self.afix and self.afix.sof:
            if self.part.sof != 11.0:
                if self.part.index > self.afix.index:
                    self.sof = self.part.sof
            else:
                self.sof = self.afix.sof
        else:
            self.sof = float(atline[5])
        try:
            x, y, z = [float(x) for x in atline[2:5]]
        except ValueError as e:
            if DEBUG:
                print(e, 'Line:', self._line_numbers[-1])
            raise ParseUnknownParam
        if abs(x) > 4:
            fvar, x = split_fvar_and_parameter(x)
            self.shx.fvars.set_fvar_usage(fvar)
        if abs(y) > 4:
            fvar, x = split_fvar_and_parameter(y)
            self.shx.fvars.set_fvar_usage(fvar)
        if abs(z) > 4:
            fvar, x = split_fvar_and_parameter(z)
            self.shx.fvars.set_fvar_usage(fvar)
        self.x = x
        self.y = y
        self.z = z
        self.xc, self.yc, self.zc = frac_to_cart(self.frac_coords, self.cell)
        if len(self.uvals) == 2 and self.shx.hklf:  # qpeaks are always behind hklf
            self.peak_height = uvals.pop()
            self.qpeak = True
        if self.shx.end:  # After 'END' can only be Q-peaks!
            self.qpeak = True
        self.sfac_num = int(atline[1])
        #self.shx.fvars.set_fvar_usage(self.fvar)

    @property
    def element(self) -> str:
        """
        >>> from structurefinder import ShelXFile
        >>> shx = ShelXFile('test-data/p21c.res')
        >>> at = shx.atoms.get_atom_by_name('C1_4')
        >>> at.sfac_num
        1
        >>> at.element
        'C'
        >>> at.element = 'O'
        >>> at.element
        'O'
        >>> at.sfac_num
        3
        """
        return self.shx.sfac2elem(self.sfac_num).capitalize()

    @property
    def an(self):
        return elements.get_atomic_number(self.element)

    @element.setter
    def element(self, new_element: str) -> None:
        """
        Sets the element type of an atom.
        """
        self.sfac_num = self.shx.elem2sfac(new_element)

    @property
    def radius(self) -> float:
        """
        Returns the atomic covalence radius in angstrom.
        """
        return elements.get_radius_from_element(self.element)

    def __iter__(self):
        for x in self.__repr__().split():
            yield x

    def __repr__(self) -> str:
        return 'Atom ID: ' + str(self.atomid)

    def __str__(self) -> str:
        """
        Returns a text line of the Atom with SHELXL syntax.
        :return: SHELX-formated atom string
        """
        if self.afix and self.shx.frag:
            # An atom from a FRAG/FEND instruction
            return Atom._fragatomstr.format(self.name, self.x, self.y, self.z)
        else:
            if len(self.uvals) > 2:
                # anisotropic atom
                try:
                    return Atom._anisatomstr.format(self.name, self.sfac_num, self.x, self.y, self.z, self.sof,
                                                    *self.uvals)
                except IndexError:
                    return 'REM Error in U values.'
            else:
                # isotropic atom:
                if self.qpeak:
                    return Atom._qpeakstr.format(self.name, self.sfac_num, self.x, self.y, self.z, self.sof, 0.04,
                                                 self.peak_height)
                try:
                    return Atom._isoatomstr.format(self.name, self.sfac_num, self.x, self.y, self.z, self.sof,
                                                   *self.uvals)
                except IndexError:
                    return Atom._isoatomstr.format(self.name, self.sfac_num, self.x, self.y, self.z, self.sof, 0.04)

    def resolve_restraints(self):
        """
        This method should generate a list of restraints objects for each restraints involved with this atom.
        TODO: Make this work
        """
        for num, r in enumerate(self.shx.restraints):
            for at in r.atoms:
                # print(r.residue_number, self.resinum, r.residue_class, self.resiclass, self.name, at)
                if r.residue_number == self.resinum and r.residue_class == self.resiclass and self.name == at:
                    self.restraints.append(r)

    @property
    def index(self):
        # The position in the res file as index number (starting from 0).
        return self.shx.index_of(self)

    @property
    def frac_coords(self, rounded=False) -> tuple:
        if rounded:
            return (round(self.x, 14), round(self.y, 14), round(self.z, 14))
        else:
            return (self.x, self.y, self.z)

    @frac_coords.setter
    def frac_coords(self, coords: list):
        self.x, self.y, self.z = coords

    @property
    def cart_coords(self):
        return [round(self.xc, 14), round(self.yc, 14), round(self.zc, 14)]

    def delete(self):
        """
        >>> from structurefinder import ShelXFile
        >>> shx = ShelXFile('./test-data/p21c.res')
        >>> at = shx.atoms.get_atom_by_id(40)
        >>> shx.atoms.all_atoms[:3]
        [Atom ID: 38, Atom ID: 40, Atom ID: 42]
        >>> at.fullname
        'C1_4'
        >>> at.delete()
        >>> shx.atoms.all_atoms[:3]
        [Atom ID: 38, Atom ID: 41, Atom ID: 43]
        """
        del self.shx.atoms[self.index]

    def to_isotropic(self) -> None:
        """
        Makes the current atom isotropic.
        """
        self.uvals = [0.04]

    '''
    def __eq__(self, other) -> bool:
        """
        Returns True if two atoms are of same name, part and residue.
        """
        if isinstance(other, str):
            return self.__repr__() == other
        if self.atomid == other.atomid:
            return True
        else:
            return False
    '''

    def find_atoms_around(self, dist=1.2, only_part=0) -> list:
        """
        Finds atoms around the current atom.
        >>> from structurefinder import ShelXFile
        >>> shx = ShelXFile('./test-data/p21c.res')
        >>> at = shx.atoms.get_atom_by_name('C1_4')
        >>> at.find_atoms_around(dist=2, only_part=2)
        [Atom ID: 38, Atom ID: 42, Atom ID: 50, Atom ID: 58]
        >>> shx.atoms.get_atom_by_name('C1_4').cart_coods
        [-0.19777464582151, 4.902748697, 6.89776640065679]
        """
        found = []
        for at in self.shx.atoms:
            if atomic_distance([self.x, self.y, self.z], [at.x, at.y, at.z], self.cell) < dist:
                # Not the atom itselv:
                if not self == at:
                    # only in special part and no q-peaks:
                    if at.part.n == only_part and not at.qpeak:
                        found.append(at)
        return found
