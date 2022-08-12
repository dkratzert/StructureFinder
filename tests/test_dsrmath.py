from structurefinder.shelxfile.dsrmath import SymmetryElement
from structurefinder.shelxfile.dsrmath import fraction_of
from structurefinder.shelxfile.shelx import ShelXFile


def test_to_fractional():
    """
    """
    assert SymmetryElement(['0.5', '0.333', '-0.5']).to_fractional() == '1/2, 1/3, -1/2'
    assert SymmetryElement(['0.5', '0.1666', '-0.5']).to_fractional() == '1/2, 1/6, -1/2'
    assert SymmetryElement(['0.6666', '0.75', '1.0']).to_fractional() == '2/3, 3/4, 1/1'


def test_to_shelxl():
    shx = ShelXFile('tests/test-data/051a/p21c.res')
    assert ['+X, +Y, +Z', '-X, 0.5+Y, 0.5-Z', '+X, -0.5-Y, -0.5+Z', '-X, -Y, -Z'] == [x.toShelxl() for x in
                                                                                      shx.symmcards]


def test_to_fractional2():
    shx = ShelXFile('tests/test-data/051a/p21c.res')
    assert [x.to_fractional() for x in shx.symmcards] == ['+X, +Y, +Z', '-X, 1/2+Y, 1/2-Z', '+X, -1/2-Y, -1/2+Z',
                                                          '-X, -Y, -Z']


def test_fraction_of_125():
    assert fraction_of(1.25) == (5, 4)


def test_fraction_of_025():
    assert fraction_of(0.25) == (1, 4)


def test_fraction_of_m125():
    assert fraction_of(-1.25) == (-5, 4)


def test_fraction_of_03():
    assert fraction_of(0.3333334) == (1, 3)


def test_fraction_of_03b():
    assert fraction_of(0.3334, precision=3) == (1, 3)
    assert fraction_of(0.3334, precision=5) is None


def test_fraction_of_050():
    assert fraction_of(0.5) == (1, 2)


def test_fraction_of_neg05():
    assert fraction_of(-0.5) == (-1, 2)
