# /usr/bin/env python
# -*- encoding: utf-8 -*-
# möp
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <dkratzert@gmx.de> wrote this file. As long as you retain
# this notice you can do whatever you want with this stuff. If we meet some day,
# and you think this stuff is worth it, you can buy me a beer in return.
# Daniel Kratzert
# ----------------------------------------------------------------------------
#

import re

atoms = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg',
         'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe',
         'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y',
         'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te',
         'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb',
         'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt',
         'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa',
         'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'D']

sorted_atoms = ['C', 'D', 'H', 'N', 'O', 'Cl', 'Br', 'I', 'F', 'S', 'P', 'Ac', 'Ag', 'Al',
                'Am', 'Ar', 'As', 'At', 'Au', 'B', 'Ba', 'Be', 'Bi', 'Bk', 'Ca', 'Cd', 'Ce',
                'Cf', 'Cm', 'Co', 'Cr', 'Cs', 'Cu', 'Dy', 'Er', 'Eu', 'Fe', 'Fr', 'Ga', 'Gd',
                'Ge', 'He', 'Hf', 'Hg', 'Ho', 'In', 'Ir', 'K', 'Kr', 'La', 'Li', 'Lu', 'Mg',
                'Mn', 'Mo', 'Na', 'Nb', 'Nd', 'Ne', 'Ni', 'Np', 'Os', 'Pa', 'Pb', 'Pd', 'Pm',
                'Po', 'Pr', 'Pt', 'Pu', 'Ra', 'Rb', 'Re', 'Rh', 'Rn', 'Ru', 'Sb', 'Sc', 'Se',
                'Si', 'Sm', 'Sn', 'Sr', 'Ta', 'Tb', 'Tc', 'Te', 'Th', 'Ti', 'Tl', 'Tm', 'U',
                'V', 'W', 'Xe', 'Y', 'Yb', 'Zn', 'Zr']

num2element = {
    0 : 'n',
    1 : 'H',
    2 : 'He',
    3 : 'Li',
    4 : 'Be',
    5 : 'B',
    6 : 'C',
    7 : 'N',
    8 : 'O',
    9 : 'F',
    10: 'Ne',
    11: 'Na',
    12: 'Mg',
    13: 'Al',
    14: 'Si',
    15: 'P',
    16: 'S',
    17: 'Cl',
    18: 'Ar',
    19: 'K',
    20: 'Ca',
    21: 'Sc',
    22: 'Ti',
    23: 'V',
    24: 'Cr',
    25: 'Mn',
    26: 'Fe',
    27: 'Co',
    28: 'Ni',
    29: 'Cu',
    30: 'Zn',
    31: 'Ga',
    32: 'Ge',
    33: 'As',
    34: 'Se',
    35: 'Br',
    36: 'Kr',
    37: 'Rb',
    38: 'Sr',
    39: 'Y',
    40: 'Zr',
    41: 'Nb',
    42: 'Mo',
    43: 'Tc',
    44: 'Ru',
    45: 'Rh',
    46: 'Pd',
    47: 'Ag',
    48: 'Cd',
    49: 'In',
    50: 'Sn',
    51: 'Sb',
    52: 'Te',
    53: 'I',
    54: 'Xe',
    55: 'Cs',
    56: 'Ba',
    57: 'La',
    58: 'Ce',
    59: 'Pr',
    60: 'Nd',
    61: 'Pm',
    62: 'Sm',
    63: 'Eu',
    64: 'Gd',
    65: 'Tb',
    66: 'Dy',
    67: 'Ho',
    68: 'Er',
    69: 'Tm',
    70: 'Yb',
    71: 'Lu',
    72: 'Hf',
    73: 'Ta',
    74: 'W',
    75: 'Re',
    76: 'Os',
    77: 'Ir',
    78: 'Pt',
    79: 'Au',
    80: 'Hg',
    81: 'Tl',
    82: 'Pb',
    83: 'Bi',
    84: 'Po',
    85: 'At',
    86: 'Rn',
    87: 'Fr',
    88: 'Ra',
    89: 'Ac',
    90: 'Th',
    91: 'Pa',
    92: 'U',
    93: 'Np',
    94: 'Pu',
    95: 'Am',
    96: 'Cm',
    97: 'Bk',
    98: 'Cf',
    99: 'Es',
}

element2num = {
    'n' : 0,
    'H' : 1,
    'D' : 1,
    'He': 2,
    'Li': 3,
    'Be': 4,
    'B' : 5,
    'C' : 6,
    'N' : 7,
    'O' : 8,
    'F' : 9,
    'Ne': 10,
    'Na': 11,
    'Mg': 12,
    'Al': 13,
    'Si': 14,
    'P' : 15,
    'S' : 16,
    'Cl': 17,
    'Ar': 18,
    'K' : 19,
    'Ca': 20,
    'Sc': 21,
    'Ti': 22,
    'V' : 23,
    'Cr': 24,
    'Mn': 25,
    'Fe': 26,
    'Co': 27,
    'Ni': 28,
    'Cu': 29,
    'Zn': 30,
    'Ga': 31,
    'Ge': 32,
    'As': 33,
    'Se': 34,
    'Br': 35,
    'Kr': 36,
    'Rb': 37,
    'Sr': 38,
    'Y' : 39,
    'Zr': 40,
    'Nb': 41,
    'Mo': 42,
    'Tc': 43,
    'Ru': 44,
    'Rh': 45,
    'Pd': 46,
    'Ag': 47,
    'Cd': 48,
    'In': 49,
    'Sn': 50,
    'Sb': 51,
    'Te': 52,
    'I' : 53,
    'Xe': 54,
    'Cs': 55,
    'Ba': 56,
    'La': 57,
    'Ce': 58,
    'Pr': 59,
    'Nd': 60,
    'Pm': 61,
    'Sm': 62,
    'Eu': 63,
    'Gd': 64,
    'Tb': 65,
    'Dy': 66,
    'Ho': 67,
    'Er': 68,
    'Tm': 69,
    'Yb': 70,
    'Lu': 71,
    'Hf': 72,
    'Ta': 73,
    'W' : 74,
    'Re': 75,
    'Os': 76,
    'Ir': 77,
    'Pt': 78,
    'Au': 79,
    'Hg': 80,
    'Tl': 81,
    'Pb': 82,
    'Bi': 83,
    'Po': 84,
    'At': 85,
    'Rn': 86,
    'Fr': 87,
    'Ra': 88,
    'Ac': 89,
    'Th': 90,
    'Pa': 91,
    'U' : 92,
    'Np': 93,
    'Pu': 94,
    'Am': 95,
    'Cm': 96,
    'Bk': 97,
    'Cf': 98,
    'Es': 99,
}

num2covradius = {
    0 : 0.5,
    1 : 0.45,
    2 : 0.45,
    3 : 1.23,
    4 : 0.90,
    5 : 0.80,
    6 : 0.77,
    7 : 0.74,
    8 : 0.71,
    9 : 0.72,
    10: 1.00,
    11: 1.54,
    12: 1.49,
    13: 1.18,
    14: 1.11,
    15: 1.06,
    16: 1.02,
    17: 0.99,
    18: 1.00,
    19: 2.03,
    20: 1.74,
    21: 1.44,
    22: 1.32,
    23: 1.22,
    24: 1.18,
    25: 1.17,
    26: 1.17,
    27: 1.16,
    28: 1.15,
    29: 1.17,
    30: 1.25,
    31: 1.26,
    32: 1.22,
    33: 1.20,
    34: 1.16,
    35: 1.14,
    36: 1.12,
    37: 2.16,
    38: 1.91,
    39: 1.62,
    40: 1.45,
    41: 1.34,
    42: 1.30,
    43: 1.27,
    44: 1.25,
    45: 1.25,
    46: 1.28,
    47: 1.34,
    48: 1.48,
    49: 1.44,
    50: 1.41,
    51: 1.40,
    52: 1.36,
    53: 1.33,
    54: 1.31,
    55: 2.35,
    56: 1.98,
    57: 1.69,
    58: 1.65,
    59: 1.65,
    60: 1.64,
    61: 1.63,
    62: 1.62,
    63: 1.85,
    64: 1.61,
    65: 1.59,
    66: 1.59,
    67: 1.58,
    68: 1.57,
    69: 1.56,
    70: 1.74,
    71: 1.56,
    72: 1.44,
    73: 1.34,
    74: 1.30,
    75: 1.28,
    76: 1.26,
    77: 1.27,
    78: 1.30,
    79: 1.34,
    80: 1.49,
    81: 1.48,
    82: 1.47,
    83: 1.46,
    84: 1.46,
    85: 1.45,
    86: 1.00,
    87: 1.00,
    88: 1.00,
    89: 1.88,
    90: 1.65,
    91: 1.61,
    92: 1.42,
    93: 1.30,
    94: 1.51,
    95: 1.82,
    96: 1.20,
    97: 1.20,
    98: 1.20,
    99: 1.20,
}

element2cov = {
    'H' : 0.45,
    'D' : 0.45,
    'He': 0.45,
    'Li': 1.23,
    'Be': 0.90,
    'B' : 0.82,
    'C' : 0.77,
    'N' : 0.75,
    'O' : 0.73,
    'F' : 0.72,
    'Ne': 0.71,
    'Na': 1.54,
    'Mg': 1.36,
    'Al': 1.18,
    'Si': 1.11,
    'P' : 1.06,
    'S' : 1.02,
    'Cl': 0.99,
    'Ar': 0.98,
    'K' : 2.03,
    'Ca': 1.74,
    'Sc': 1.44,
    'Ti': 1.32,
    'V' : 1.22,
    'Cr': 1.18,
    'Mn': 1.17,
    'Fe': 1.17,
    'Co': 1.16,
    'Ni': 1.15,
    'Cu': 1.17,
    'Zn': 1.25,
    'Ga': 1.26,
    'Ge': 1.22,
    'As': 1.2,
    'Se': 1.16,
    'Br': 1.14,
    'Kr': 1.12,
    'Rb': 2.16,
    'Sr': 1.91,
    'Y' : 1.62,
    'Zr': 1.45,
    'Nb': 1.34,
    'Mo': 1.3,
    'Tc': 1.27,
    'Ru': 1.25,
    'Rh': 1.25,
    'Pd': 1.28,
    'Ag': 1.34,
    'Cd': 1.48,
    'In': 1.44,
    'Sn': 1.41,
    'Sb': 1.4,
    'Te': 1.36,
    'I' : 1.33,
    'Xe': 1.31,
    'Cs': 2.35,
    'Ba': 1.98,
    'La': 1.69,
    'Ce': 1.65,
    'Pr': 1.65,
    'Nd': 1.64,
    'Pm': 1.63,
    'Sm': 1.62,
    'Eu': 1.85,
    'Gd': 1.61,
    'Tb': 1.59,
    'Dy': 1.59,
    'Ho': 1.58,
    'Er': 1.57,
    'Tm': 1.56,
    'Yb': 1.74,
    'Lu': 1.56,
    'Hf': 1.44,
    'Ta': 1.34,
    'W' : 1.3,
    'Re': 1.28,
    'Os': 1.26,
    'Ir': 1.27,
    'Pt': 1.3,
    'Au': 1.34,
    'Hg': 1.49,
    'Tl': 1.48,
    'Pb': 1.47,
    'Bi': 1.46,
    'Po': 1.46,
    'At': 1.45,
    'Rn': 1.0,
    'Fr': 1.0,
    'Ra': 1.0,
    'Ac': 1.88,
    'Th': 1.65,
    'Pa': 1.61,
    'U' : 1.42,
    'Np': 1.30,
    'Pu': 1.51,
    'Am': 1.82,
    'Cm': 1.20,
    'Bk': 1.20,
    'Cf': 1.20,
    'Es': 1.20,
}

element2color = {
    'H' : "#FFFFFF",
    'He': "#FFFFFF",
    'Li': "#CC80FF",
    'Be': "#c9d5e9",
    'B' : "#FFB5B5",
    'C' : "#797979",
    'N' : "#3050F8",
    'O' : "#FF0D0D",
    'F' : "#90e001",
    'Ne': "#B3E3F5",
    'Na': "#AB5CF2",
    'Mg': "#bbc7db",
    'Al': "#BFA6A6",
    'Si': "#F0C8A0",
    'P' : "#FF8000",
    'S' : "#eeee2c",
    'Cl': "#419941",
    'Ar': "#80D1E3",
    'K' : "#8F40D4",
    'Ca': "#bbc7db",
    'Sc': "#E6E6E6",
    'Ti': "#BFC2C7",
    'V' : "#A6A6AB",
    'Cr': "#8A99C7",
    'Mn': "#9C7AC7",
    'Fe': "#E06633",
    'Co': "#F090A0",
    'Ni': "#50D050",
    'Cu': "#C88033",
    'Zn': "#7D80B0",
    'Ga': "#C28F8F",
    'Ge': "#668F8F",
    'As': "#BD80E3",
    'Se': "#FFA100",
    'Br': "#A62929",
    'Kr': "#5CB8D1",
    'Rb': "#702EB0",
    'Sr': "#bbc7db",
    'Y' : "#94FFFF",
    'Zr': "#94E0E0",
    'Nb': "#73C2C9",
    'Mo': "#54B5B5",
    'Tc': "#3B9E9E",
    'Ru': "#248F8F",
    'Rh': "#0A7D8C",
    'Pd': "#006985",
    'Ag': "#C0C0C0",
    'Cd': "#FFD98F",
    'In': "#A67573",
    'Sn': "#668080",
    'Sb': "#9E63B5",
    'Te': "#D47A00",
    'I' : "#940094",
    'Xe': "#429EB0",
    'Cs': "#57178F",
    'Ba': "#bbc7db",
    'La': "#d9ffff",
    'Ce': "#d9ffff",
    'Pr': "#d9ffff",
    'Nd': "#d9ffff",
    'Pm': "#d9ffff",
    'Sm': "#d9ffff",
    'Eu': "#d9ffff",
    'Gd': "#d9ffff",
    'Tb': "#d9ffff",
    'Dy': "#d9ffff",
    'Ho': "#d9ffff",
    'Er': "#d9ffff",
    'Tm': "#d9ffff",
    'Yb': "#d9ffff",
    'Lu': "#d9ffff",
    'Hf': "#d9ffff",
    'Ta': "#d9ffff",
    'W' : "#d9ffff",
    'Re': "#d9ffff",
    'Os': "#d9ffff",
    'Ir': "#d9ffff",
    'Pt': "#d9ffff",
    'Au': "#d9ffff",
    'Hg': "#d9ffff",
    'Tl': "#d9ffff",
    'Pb': "#d9ffff",
    'Bi': "#d9ffff",
    'Po': "#d9ffff",
    'At': "#d9ffff",
    'Rn': "#d9ffff",
    'Fr': "#d9ffff",
    'Ra': "#d9ffff",
    'Ac': "#d9ffff",
    'Th': "#d9ffff",
    'Pa': "#d9ffff",
    'U' : "#d9ffff",
    'Np': "#d9ffff",
    'Pu': "#d9ffff",
    'Am': "#d9ffff",
    'Cm': "#d9ffff",
    'Bk': "#d9ffff",
    'Cf': "#d9ffff",
    'D' : "#e2e6e6",
}


def get_element_color(element: str) -> str:
    """
    Retruns RGB color code in Hex for the element.
    """
    return element2color.get(element.capitalize())


def get_radius(atomic_number: int) -> float:
    """
    Get the covalent radius in pm for the element.
    """
    return num2covradius[atomic_number]


def get_radius_from_element(element: str) -> float:
    """
    Returns the radius of an atom by its element name.
    """
    try:
        return element2cov[element]
    except KeyError:
        return 0.8


def get_atomic_number(element: str) -> int:
    """
    returns the atomic number from the element symbol
    """
    return element2num[element]


def get_element(atomic_number: int) -> str:
    """
    returns the element symbol from the atomic number
    """
    return num2element[atomic_number]


def get_atomlabel(input_atom: str) -> str:
    """
    converts an atom name like C12 to the element symbol C.
    """
    atom = ''
    for x in input_atom:  # iterate over characters in i
        if re.match(r'^[A-Za-z#]', x):  # Alphabet and "#" as allowed characters in names
            atom = atom + x.upper()  # add characters to atoms until numbers occur
        else:  # now we have atoms like C, Ca, but also Caaa
            break
    try:
        if atom[0:2].capitalize() in atoms:  # fixes names like Caaa to be just Ca
            return atom[0:2].capitalize()  # atoms first, search for all two-letter atoms
        elif atom[0].upper() in atoms:
            return atom[0]  # then for all one-letter atoms
        else:
            # print('*** {} is not a valid atom!! ***'.format(atom))
            raise KeyError
    except(IndexError):
        # print('*** {} is not a valid atom! ***'.format(atom))
        raise KeyError


if __name__ == '__main__':
    pass
