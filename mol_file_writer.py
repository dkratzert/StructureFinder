"""
benzene
ACD/Labs0812062058

 6  6  0  0  0  0  0  0  0  0  1 V2000
   1.9050   -0.7932    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   1.9050   -2.1232    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   0.7531   -0.1282    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   0.7531   -2.7882    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  -0.3987   -0.7932    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  -0.3987   -2.1232    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
 2  1  1  0  0  0  0
 3  1  2  0  0  0  0
 4  2  2  0  0  0  0
 5  3  1  0  0  0  0
 6  4  1  0  0  0  0
 6  5  2  0  0  0  0
M  END
$$$$

1-3	  Header
1		        Molecule name ("benzene")
2		        User/Program/Date/etc information
3		        Comment (blank)
4-17  Connection table (Ctab)
4		        Counts line: 6 atoms, 6 bonds, ..., V2000 standard
5-10		    Atom block (1 line for each atom): x, y, z (in angstroms), element, etc.
11-16		    Bond block (1 line for each bond): 1st atom, 2nd atom, type, etc.
17		        Properties block (empty)
18	  $$$$
"""
import os


class MolFile():
    """
    This mol file writer is only to use the file with JSmol, not to implement the standard exactly!
    """
    def __init__(self, cif):
        self.cif = cif

    def header(self) -> str:
        """
        For JSmol, I don't need a facy header.
        """
        return "\n\n\n"

    def connection_table(self) -> str:
        """
          6  6  0  0  0  0  0  0  0  0  1 V2000
        """
        atoms = 6
        bonds = 6

        tab = "  {1}  {2}  {3}  {4}  {5}  {6}  {7}  {8}  {9}  {10}  {11}  {12}".format(
            atoms, bonds, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, "V2000"
        )
        return tab

    def atoms(self):
        """
        """
        atoms = []
        x = ''
        y = ''
        z = ''
        element = ''
        zeros = "0  0  0  0  0  0  0  0  0  0  0  0"
        for i in self.cif.atoms:
            atoms.append("   {:>6.4}   {:>6.4}    {:>6.4} {}   {}").format(x, y, z, element, zeros)
        return os.linesep.join(atoms)

    def bonds(self):
        """
        """
        

    def make_mol(self):
        """
        """
        return mol