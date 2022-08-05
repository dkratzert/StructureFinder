
# TODO:
# Calculate real space group from symm cards during indexing
# use following cell comparison
# store niggli cell during indexing

import gemmi
cell = gemmi.UnitCell(13.738, 14.735, 16.598, 116.361, 97.813, 90.693)
sg = gemmi.SpaceGroup('P 1')
gv = gemmi.GruberVector(cell, sg)

cell2 = gemmi.UnitCell(10.360, 18.037, 25.764, 127.030, 129.810, 90.510)
sg2 = gemmi.SpaceGroup('P 1')
gv2 = gemmi.GruberVector(cell2, sg2)

gv.niggli_reduce()
gv2.niggli_reduce()

gv.get_cell()
# <gemmi.UnitCell(13.738, 14.735, 16.5958, 63.6541, 81.5645, 89.307)>
gv2.get_cell()
# <gemmi.UnitCell(10.36, 12.9807, 18.037, 100.37, 90.51, 108.246)>

gvc = gv.get_cell()
gvc.approx(gv2.get_cell(), 0.0001)
# False

gvc.is_similar(gv2.get_cell(), rel=0.1, deg=2.5)
# True

sv = gemmi.SellingVector(cell, sg)
sv2 = gemmi.SellingVector(cell2, sg2)

sv2.reduce()
# 3
sv.reduce()
# 1
sv.sort()
sv2.sort()
print(sv)
# <gemmi.SellingVector((-108.60, -31.00, -2.45, -155.29, -106.08, -135.90))>
print(sv2)
# <gemmi.SellingVector((-42.15, -1.66, -42.11, -63.56, -84.25, -281.52))>

sv.sum_b_squared()
# 1078.609162185184
sv2.sum_b_squared()
# 1030.492643465581
