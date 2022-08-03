# -*- coding: utf-8 -*-
"""
Created on 03.10.2017

 ----------------------------------------------------------------------------
* "THE BEER-WARE LICENSE" (Revision 42):
* <dkratzert@gmx.de> wrote this file. As long as you retain this
* notice you can do whatever you want with this stuff. If we meet some day, and
* you think this stuff is worth it, you can buy me a beer in return.
* ----------------------------------------------------------------------------

@author: Daniel Kratzert
"""
from structurefinder.searcher.database_handler import StructureTable
from structurefinder.searcher.fileparser import CifFile


class Lattice(object):
    def __init__(self, atoms: list, symmcards: list, cell: list):
        """
        Atoms:
        [(label, float(x), float(x), float(x)), (label, x, y, z), ...]
        Symmcards from cif file, e.g.:
        ['x, y, z', '-x, y+1/2, -z+1/2', '-x, -y, -z', 'x, -y-1/2, z-1/2']
        """
        self.cell = cell
        self.atoms = atoms
        self.symmcards = [x.replace("/", "./") for x in (i for i in symmcards)]

    def pack_structure(self):
        """
        Grows the atoms according to symmetry.

        This approach is way too slow to be useful!
        """
        # Make sure that all atoms are in the unit cell:
        for i in range(len(self.atoms)):
            (name, symbol, xn, yn, zn) = self.atoms[i]
            xn = (xn + 10) % 1.0
            yn = (yn + 10) % 1.0
            zn = (zn + 10) % 1.0
            # name = get_atomlabel(name)  # name is now the atomic symbol
            self.atoms[i] = (name, symbol, xn, yn, zn)
        mindist = 0.01  # Angstrom
        # For each atom, apply each symmetry operation to create a new atom.
        imax = len(self.atoms)
        i = 0
        # maxmax = 20 * imax
        while i < imax:
            name, at_type, x, y, z = self.atoms[i]
            for op in self.symmcards:
                if not op.strip():
                    continue
                try:
                    xn, yn, zn = eval(op)
                except SyntaxError:
                    continue
                # Make sure that the new atom lies within the unit cell.
                xn = (xn + 10) % 1.0
                yn = (yn + 10) % 1.0
                zn = (zn + 10) % 1.0
                # Check if the new position is actually new, or the same as a previous atom.
                new_atom = True
                for at in self.atoms:
                    if abs(at[2] - xn) < mindist and abs(at[3] - yn) < mindist and abs(at[4] - zn) < mindist:
                        new_atom = False
                        # Check that this is the same atom type.
                        if at[1] != at_type:
                            # print("{}, {}".format(at[0], at_type))
                            break
                            # print('Invalid atom found')
                # If the atom is new, add it to the list:
                if new_atom:
                    self.atoms.append((name, at_type, xn, yn, zn))
            # Update the loop iterator.
            i = i + 1
            imax = len(self.atoms)
            # if imax > maxmax:
            #    break  # break after too many iterations
        return self.atoms


if __name__ == '__main__':
    import gemmi
    cif = CifFile()
    fullpath = 'tests/test-data/p-1_a.cif'
    doc = gemmi.cif.Document()
    doc.source = fullpath
    doc.parse_file(fullpath)
    cifok = cif.parsefile(doc)
    # pprint(cif.cif_data)
    # print(cifok)
    db = StructureTable('./structuredb.sqlite')
    db.database.initialize_db()
    ats = db.get_atoms_table(263, cartesian=False)
    cards = db.get_row_as_dict(263)['_space_group_symop_operation_xyz'].replace("'", "").split("\n")
    print(cards)
    l = Lattice(ats, cards, cif.cell)
    gr = l.pack_structure()
    for i in gr:
        print(i)
