from structurefinder.shelxfile.dsrmath import SymmetryElement
from structurefinder.shelxfile.shelx import ShelXFile


def test_to_fractional():
    """
    """
    assert SymmetryElement(['0.5', '0.33', '-0.5']).to_fractional() == '1/2, 1/3, -1/2'
    assert SymmetryElement(['0.5', '0.166', '-0.5']).to_fractional() == '1/2, 1/6, -1/2'
    assert SymmetryElement(['0.666', '0.75', '1.0']).to_fractional() == '2/3, 3/4, '


def test_to_shelxl():
    shx = ShelXFile('tests/test-data/051a/p21c.res')
    assert ['+X, +Y, +Z', '-X, 0.5+Y, 0.5-Z', '+X, -0.5-Y, -0.5+Z', '-X, -Y, -Z'] == [x.toShelxl() for x in
                                                                                      shx.symmcards]


def test_to_fractional2():
    shx = ShelXFile('tests/test-data/051a/p21c.res')
    assert [x.to_fractional() for x in shx.symmcards] == ['+X, +Y, +Z', '-X, 1/2+Y, 1/2-Z', '+X, -1/2-Y, -1/2+Z',
                                                          '-X, -Y, -Z']
