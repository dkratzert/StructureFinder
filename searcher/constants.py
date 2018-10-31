import sys
py36 = False
py34 = False
py2 = False

if sys.version_info > (3, 4, 5):
    py36 = True
elif sys.version_info > (3, 4):
    py34 = True
elif sys.version_info < (3, 0) >= (2, 7):
    py2 = True

centering_num_2_letter = {0: 'P', 1: 'A', 2: 'B', 3: 'C', 4: 'F', 5: 'I', 6: 'R'}
centering_letter_2_num = {'P': 0, 'A': 1, 'B': 2, 'C': 3, 'F': 4, 'I': 5, 'R': 6}

atoms = ('D', 'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg',
         'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe',
         'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y',
         'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te',
         'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb',
         'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt',
         'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa',
         'U')

celltxt = """
   <html><head/><body>
   <table border="0" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;" 
          cellspacing="1" cellpadding="1">
       <tr>
           <td><p align="left"><span style=" font-style:italic;">a</span> = </p></td>
           <td><p align="right">{:>8.3f} Å, </p></td>
           <td><p align="right"><span style="font-style:italic;">&alpha;</span> = </p></td> 
           <td><p align="right">{:>8.3f}° </p></td>
       </tr>
       <tr>
           <td><p align="left"><span style=" font-style:italic;">b</span> = </p></td>
           <td><p align="right">{:>8.3f} Å, </p></td>
           <td><p align="right"><span style=" font-style:italic;">&beta;</span> = </p></td> 
           <td><p align="right">{:>8.3f}° </p></td>
       </tr>
       <tr>
           <td><p align="left"><span style=" font-style:italic;">c</span> = </p></td>
           <td><p align="right">{:>8.3f} Å, </p></td>
           <td><p align="right"><span style=" font-style:italic;">&gamma;</span> = </p></td> 
           <td><p align="right">{:>8.3f}° </p></td>
       </tr>
   </table>
   Volume = {:8.2f} Å<sup>3</sup>, <b>{}</b>
   </body></html>
   """
