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
   Volume = {:8.2f} Å<sup>3   
   </body></html>
   """
