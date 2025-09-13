import unittest
import gemmi

from structurefinder.searcher.cif_file import CifFile


class TestParser(unittest.TestCase):
    def setUp(self) -> None:
        self.cif = CifFile()

    def test_file1(self):
        fullpath = r'tests/test-data/668839.cif'
        doc = gemmi.cif.Document()
        doc.source = fullpath
        doc.parse_file(fullpath)
        cifok = self.cif.parsefile(doc)
        self.assertEqual(True, cifok)
        self.assertEqual(69, len(list(self.cif.atoms)))
