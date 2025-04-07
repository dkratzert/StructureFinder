import unittest

from structurefinder.searcher.misc import get_list_of_elements, format_sum_formula, is_a_nonzero_file, \
    get_error_from_value
from shelxfile.refine import range_resolver, wrap_line, multiline_test, chunks


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

class Test(unittest.TestCase):
    def test_range_resolver_1(self):
        r = "C2 > C5".split()
        atlist = 'C1 C2 C3 C4 C5'.split()
        self.assertEqual(['C2', 'C3', 'C4', 'C5'], range_resolver(r, atlist))

    def test_range_resolver_2(self):
        r = "C2_2 > C5_2".split()
        atlist = 'C1_1 C1_2 C2_2 C3_2 C4_2 C5_2'.split()
        self.assertEqual(['C2_2', 'C3_2', 'C4_2', 'C5_2'], range_resolver(r, atlist))

    def test_range_resolver_3(self):
        r = "C2_1 > C5_1".split()
        atlist = 'C1_1 C1_2 C2_2 C3_2 C4_2 C5_2'.split()
        with self.assertRaises(ValueError):
            range_resolver(r, atlist)

    def test_wrap_line(self):
        self.assertEqual('This is a really long line with over 79 characters. Shelxl wants it to be  =\n   wrapped.',
                         wrap_line(
                             "This is a really long line with over 79 characters. Shelxl wants it to be wrapped."))

    def test_multiline_test1(self):
        line = 'C1    1    0.278062    0.552051    0.832431    11.00000    0.02895    0.02285 ='
        self.assertEqual(True, multiline_test(line))

    def test_multiline_test2(self):
        line = 'C1    1    0.278062    0.552051    0.832431    11.00000    0.05 '
        self.assertEqual(False, multiline_test(line))

    def test_chunks(self):
        l = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 'a', 'b', 'c', 'd', 'e', 'f']
        self.assertEqual([[1, 2, 3, 4, 5], [6, 7, 8, 9, 0], ['a', 'b', 'c', 'd', 'e'], ['f']], chunks(l, 5))
        self.assertEqual([[1], [2], [3], [4], [5], [6], [7], [8], [9], [0], ['a'], ['b'], ['c'], ['d'], ['e'], ['f']],
                         chunks(l, 1))
        self.assertEqual([[1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 'a', 'b', 'c', 'd', 'e', 'f']], chunks(l, 50))


class FileTestCase(unittest.TestCase):
    def test_existing_nonzero_file(self):
        filepath = './src/structurefinder/searcher/misc.py'
        self.assertTrue(is_a_nonzero_file(filepath))

    def test_existing_zero_file(self):
        filepath = './tests/test-data/test_zerofile.cif'
        self.assertFalse(is_a_nonzero_file(filepath))

    def test_nonexistent_file(self):
        filepath = 'foo.bar'
        self.assertFalse(is_a_nonzero_file(filepath))

    def test_existing_nonzero_file_another(self):
        filepath = './src/structurefinder/strf.py'
        self.assertTrue(is_a_nonzero_file(filepath))


class TestGetErrorFromValue(unittest.TestCase):
    def test_get_error_from_value_with_error(self):
        self.assertEqual(get_error_from_value("0.0123 (23)"), (0.0123, 0.0023))
        self.assertEqual(get_error_from_value("0.0123(23)"), (0.0123, 0.0023))
        self.assertEqual(get_error_from_value("250.0123(23)"), (250.0123, 0.0023))
        self.assertEqual(get_error_from_value("123(25)"), (123.0, 25.0))
        self.assertEqual(get_error_from_value("123(25"), (123.0, 25.0))

    def test_get_error_from_value_without_error(self):
        self.assertEqual(get_error_from_value('0.0123'), (0.0123, 0.0))
        self.assertEqual(get_error_from_value("abc"), (0.0, 0.0))

    def test_get_error_from_value_empty_string(self):
        self.assertEqual(get_error_from_value(""), (0.0, 0.0))

    def test_get_error_from_value_invalid_format(self):
        self.assertEqual(get_error_from_value("0.0123()"), (0.0123, 0.0))
        with self.assertRaises(ValueError):
            self.assertEqual(get_error_from_value("0.0123 (abc)"), (0.0123, 0.0))
        self.assertEqual(get_error_from_value("0.0123 (123)"), (0.0123, 0.0123))
        self.assertEqual(get_error_from_value("0.0123 (23"), (0.0123, 0.0023))
        self.assertEqual(get_error_from_value("0.0123("), (0.0123, 0.0))
        self.assertEqual(get_error_from_value("0.0123)"), (0.0, 0.0))
        self.assertEqual(get_error_from_value("0.0123("), (0.0123, 0.0))
        with self.assertRaises(ValueError):
            self.assertEqual(get_error_from_value("0.0123((23))"), (0.0123, 0.0))
        with self.assertRaises(ValueError):
            self.assertEqual(get_error_from_value("(23)"), (0.0, 0.0))
        with self.assertRaises(ValueError):
            self.assertEqual(get_error_from_value("0.0123(23.45)"), (0.0123, 0.0))
        self.assertEqual(get_error_from_value("0.0123(23)abc"), (0.0123, 0.0023))


if __name__ == '__main__':
    unittest.main()





