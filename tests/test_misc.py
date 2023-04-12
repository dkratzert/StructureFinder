import unittest

from structurefinder.searcher.misc import get_list_of_elements, format_sum_formula


class TestListOfElements(unittest.TestCase):
    def test_get_list_of_elements_SCL(self):
        self.assertEqual(['S', 'Cl'], get_list_of_elements("SCl"))

    def test_get_list_of_elements_S1CL1(self):
        self.assertEqual(['S', 'Cl'], get_list_of_elements("S1Cl1"))

    def test_get_list_of_elements_S1CL(self):
        self.assertEqual(['S', 'Cl'], get_list_of_elements("S1Cl"))

    def test_get_list_of_elements_ScCl(self):
        self.assertEqual(['Sc', 'Cl'], get_list_of_elements("ScCl"))

    def test_get_list_of_elements_S20_CL(self):
        self.assertEqual(['S', 'Cl'], get_list_of_elements("S20 Cl"))


class TestFormatSumForm(unittest.TestCase):
    def test_format(self):
        self.assertEqual('<html><body>C<sub>12 </sub>H<sub>6 </sub>O<sub>3 </sub>Mn<sub>7 </sub></body></html>',
                         format_sum_formula({'C': 12, 'H': 6, 'O': 3, 'Mn': 7}))
