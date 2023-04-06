import unittest

from structurefinder.searcher.misc import get_list_of_elements


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
