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
    <html>
    <body>
    <div align="right">
        <table border="0" cellspacing="1" cellpadding="1" style='font-size: 12px'>
            <tr>
                <td align='right'><i>a</i> = </td>
                <td align='right'>{:>7.3f} Å,</td>
                <td align='right'><i>&alpha;</i> = </td> 
                <td align='right'>{:>7.3f}°</td>
            </tr>
            <tr>
                <td align='right'><i>b</i> = </td>
                <td align='right'>{:>7.3f} Å,</td>
                <td align='right'><i>&beta;</i> = </td> 
                <td align='right'>{:>7.3f}°</td>
            </tr>
            <tr>
                <td align='right'><i>c</i> = </td>
                <td align='right'>{:>7.3f} Å,</td>
                <td align='right'><i>&gamma;</i> = </td> 
                <td align='right'>{:>7.3f}°</td>
            </tr>
       </table>
   </div>
   <div align='right' style="margin-left:0">
    Volume = {:8.2f} Å<sup>3</sup>, <b>{}</b>
   </div>
   </body>
   </html>
    """


