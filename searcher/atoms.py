import re

atoms = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg',
         'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe',
         'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y',
         'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te',
         'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb',
         'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt',
         'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa',
         'U']

element_base = {
    # number: name symbol ions
    # 0: ['Neutron',     'n',  ()],
    1  : ['Hydrogen', 'H', (1,)],
    2  : ['Helium', 'He', ()],
    3  : ['Lithium', 'Li', (1,)],
    4  : ['Beryllium', 'Be', (2,)],
    5  : ['Boron', 'B', (3,)],
    6  : ['Carbon', 'C', (2, -4, 4)],
    7  : ['Nitrogen', 'N', (2, -3, 3, 4, 5)],
    8  : ['Oxygen', 'O', (-2,)],
    9  : ['Fluorine', 'F', (-1,)],
    10 : ['Neon', 'Ne', ()],
    11 : ['Sodium', 'Na', (1,)],
    12 : ['Magnesium', 'Mg', (2,)],
    13 : ['Aluminum', 'Al', (3,)],
    14 : ['Silicon', 'Si', (4,)],
    15 : ['Phosphorus', 'P', (-3, 3, 4, 5)],
    16 : ['Sulfur', 'S', (-2, 2, 4, 6)],
    17 : ['Chlorine', 'Cl', (-1, 1, 3, 5, 7)],
    18 : ['Argon', 'Ar', ()],
    19 : ['Potassium', 'K', (1,)],
    20 : ['Calcium', 'Ca', (2,)],
    21 : ['Scandium', 'Sc', (3,)],
    22 : ['Titanium', 'Ti', (3, 4)],
    23 : ['Vanadium', 'V', (2, 3, 4, 5)],
    24 : ['Chromium', 'Cr', (2, 3, 6)],
    25 : ['Manganese', 'Mn', (2, 3, 4, 6, 7)],
    26 : ['Iron', 'Fe', (2, 3)],
    27 : ['Cobalt', 'Co', (2, 3)],
    28 : ['Nickel', 'Ni', (2, 3)],
    29 : ['Copper', 'Cu', (1, 2)],
    30 : ['Zinc', 'Zn', (2,)],
    31 : ['Gallium', 'Ga', (3,)],
    32 : ['Germanium', 'Ge', (4,)],
    33 : ['Arsenic', 'As', (-3, 3, 5)],
    34 : ['Selenium', 'Se', (-2, 4, 6)],
    35 : ['Bromine', 'Br', (-1, 1, 5)],
    36 : ['Krypton', 'Kr', ()],
    37 : ['Rubidium', 'Rb', (1,)],
    38 : ['Strontium', 'Sr', (2,)],
    39 : ['Yttrium', 'Y', (3,)],
    40 : ['Zirconium', 'Zr', (4,)],
    41 : ['Niobium', 'Nb', (3, 5)],
    42 : ['Molybdenum', 'Mo', (2, 3, 4, 5, 6)],
    43 : ['Technetium', 'Tc', (7,)],
    44 : ['Ruthenium', 'Ru', (2, 3, 4, 6, 8)],
    45 : ['Rhodium', 'Rh', (2, 3, 4)],
    46 : ['Palladium', 'Pd', (2, 4)],
    47 : ['Silver', 'Ag', (1,)],
    48 : ['Cadmium', 'Cd', (2,)],
    49 : ['Indium', 'In', (3,)],
    50 : ['Tin', 'Sn', (2, 4)],
    51 : ['Antimony', 'Sb', (-3, 3, 5)],
    52 : ['Tellurium', 'Te', (-2, 4, 6)],
    53 : ['Iodine', 'I', (-1, 1, 5, 7)],
    54 : ['Xenon', 'Xe', ()],
    55 : ['Cesium', 'Cs', (1,)],
    56 : ['Barium', 'Ba', (2,)],
    57 : ['Lanthanum', 'La', (3,)],
    58 : ['Cerium', 'Ce', (3, 4)],
    59 : ['Praseodymium', 'Pr', (3, 4)],
    60 : ['Neodymium', 'Nd', (3,)],
    61 : ['Promethium', 'Pm', (3,)],
    62 : ['Samarium', 'Sm', (2, 3)],
    63 : ['Europium', 'Eu', (2, 3)],
    64 : ['Gadolinium', 'Gd', (3,)],
    65 : ['Terbium', 'Tb', (3, 4)],
    66 : ['Dysprosium', 'Dy', (3,)],
    67 : ['Holmium', 'Ho', (3,)],
    68 : ['Erbium', 'Er', (3,)],
    69 : ['Thulium', 'Tm', (2, 3)],
    70 : ['Ytterbium', 'Yb', (2, 3)],
    71 : ['Lutetium', 'Lu', (3,)],
    72 : ['Hafnium', 'Hf', (4,)],
    73 : ['Tantalum', 'Ta', (5,)],
    74 : ['Tungsten', 'W', (2, 3, 4, 5, 6)],
    75 : ['Rhenium', 'Re', (-1, 2, 4, 6, 7)],
    76 : ['Osmium', 'Os', (2, 3, 4, 6, 8)],
    77 : ['Iridium', 'Ir', (2, 3, 4, 6)],
    78 : ['Platinum', 'Pt', (2, 4)],
    79 : ['Gold', 'Au', (1, 3)],
    80 : ['Mercury', 'Hg', (1, 2)],
    81 : ['Thallium', 'Tl', (1, 3)],
    82 : ['Lead', 'Pb', (2, 4)],
    83 : ['Bismuth', 'Bi', (3, 5)],
    84 : ['Polonium', 'Po', (2, 4)],
    85 : ['Astatine', 'At', (-1, 1, 3, 5, 7)],
    86 : ['Radon', 'Rn', ()],
    87 : ['Francium', 'Fr', (1,)],
    88 : ['Radium', 'Ra', (2,)],
    89 : ['Actinium', 'Ac', (3,)],
    90 : ['Thorium', 'Th', (4,)],
    91 : ['Protactinium', 'Pa', (4, 5)],
    92 : ['Uranium', 'U', (3, 4, 5, 6)],
    93 : ['Neptunium', 'Np', (3, 4, 5, 6)],
    94 : ['Plutonium', 'Pu', (3, 4, 5, 6)],
    95 : ['Americium', 'Am', (3, 4, 5, 6)],
    96 : ['Curium', 'Cm', (3,)],
    97 : ['Berkelium', 'Bk', (3, 4)],
    98 : ['Californium', 'Cf', (3,)],
    99 : ['Einsteinium', 'Es', (3,)],
    100: ['Fermium', 'Fm', (3,)],
    101: ['Mendelevium', 'Md', (2, 3)],
    102: ['Nobelium', 'No', (2, 3)],
    103: ['Lawrencium', 'Lr', (3,)],
    104: ['Rutherfordium', 'Rf', (4,)],
    105: ['Dubnium', 'Db', ()],
    106: ['Seaborgium', 'Sg', ()],
    107: ['Bohrium', 'Bh', ()],
    108: ['Hassium', 'Hs', ()],
    109: ['Meitnerium', 'Mt', ()],
    110: ['Darmstadtium', 'Ds', ()],
    111: ['Roentgenium', 'Rg', ()],
    112: ['Copernicium', 'Cn', ()],
    114: ['Ununquadium', 'Uuq', ()],
    116: ['Ununhexium', 'Uuh', ()],
}


def get_atomlabel(input_atom):
    """
    converts an atom name like C12 to the element symbol C
    """
    elements = [x.upper() for x in atoms]
    atom = ''
    for x in input_atom:  # iterate over characters in i
        if re.match(r'^[A-Za-z#]', x):  # Alphabet and "#" as allowed characters in names
            atom = atom + x.upper()  # add characters to atoms until numbers occur
        else:  # now we have atoms like C, Ca, but also Caaa
            break
    try:
        if atom[0:2] in elements:  # fixes names like Caaa to be just Ca
            return atom[0:2]  # atoms first, search for all two-letter atoms
        elif atom[0] in elements:
            return atom[0]  # then for all one-letter atoms
        else:
            # print('*** {} is not a valid atom!! ***'.format(atom))
            return input_atom
    except IndexError:
        # print('*** {} is not a valid atom! ***'.format(atom))
        return input_atom


class Element():
    def __init__(self):
        self.element_base = element_base

    def get_atomic_number(self, element):
        """
        returns the atomic number from the element symbol

        :param element:
        :type element:

        >>> el = Element()
        >>> el.get_atomic_number('F')
        9
        """
        for atomic_number, elements in list(self.element_base.items()):
            if element.upper() == elements[1].upper():
                return (atomic_number)

    def get_element(self, atomic_number):
        """
        returns the element symbol from the atomic number

        :param atomic_number: atomic number
        :type atomic_number: integer

        >>> el = Element()
        >>> el.get_element(7)
        'N'
        """
        return self.element_base[atomic_number][1]


if __name__ == '__main__':
    import doctest

    failed, attempted = doctest.testmod()  # verbose=True)
    if failed == 0:
        print('passed all {} tests!'.format(attempted))
    else:
        print('{} of {} tests failed'.format(failed, attempted))
