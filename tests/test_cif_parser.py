import unittest
from pathlib import Path

from searcher.fileparser import Cif


class TestParser(unittest.TestCase):
    def setUp(self) -> None:
        self.cif = Cif()

    def test_file1(self):
        cifok = self.cif.parsefile(Path('test-data/668839.cif').read_text().splitlines(keepends=True))
        self.assertEqual(True, cifok)
        self.assertEqual(69, len(list(self.cif.atoms)))