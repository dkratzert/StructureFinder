import unittest

from structurefinder.searcher.misc import get_list_of_elements, format_sum_formula, is_a_nonzero_file, \
    get_error_from_value


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
