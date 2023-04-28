import unittest

from structurefinder.searcher.misc import get_value


class TestGetValue(unittest.TestCase):
    def test_get_value_empty_brackets(self):
        self.assertEqual(1.123, get_value('1.123()'))

    def test_get_value_with_error_value(self):
        self.assertEqual(1.123, get_value('1.123(56)'))

    def test_get_value_no_open_bracket(self):
        self.assertRaises(ValueError, get_value, '1.123)')

    def test_get_value_no_closing_bracket(self):
        self.assertEqual(1.123, get_value('1.123('))


if __name__ == "__main__":
    unittest.main()
