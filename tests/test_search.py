import unittest

from pymatgen.core import lattice
from searcher import database_handler
from searcher.misc import regular_results_parameters, more_results_parameters
from structurefinder.shelxfile import vol_unitcell


class TestSearch(unittest.TestCase):
    def setUp(self) -> None:
        self.dbfilename = 'test-data/test.sql'
        self.structures = database_handler.StructureTable(self.dbfilename)

    def test_cellfind(self):
        idlist = []
        cell = [10.930, 12.716, 15.709, 90.000, 90.000, 90.000]
        results = [(260, 10.93, 12.7162, 15.7085, 90.0, 90.0, 90.0, 2183.3)]
        volume = vol_unitcell(*cell)
        atol, ltol, vol_threshold = regular_results_parameters(volume)
        cells = self.structures.find_by_volume(volume, vol_threshold)
        self.assertEqual(results, cells)
        lattice1 = lattice.Lattice.from_parameters(*cell)
        for curr_cell in cells:
            try:
                lattice2 = lattice.Lattice.from_parameters(*curr_cell[1:7])
            except ValueError:
                continue
            mapping = lattice1.find_mapping(lattice2, ltol, atol, skip_rotation_matrix=True)
            if mapping:
                idlist.append(curr_cell[0])
        self.assertEqual(idlist, [260])

    def test_more_results_cellfind(self):
        idlist = []
        cell = [10.930, 12.716, 15.709, 90.000, 90.000, 90.000]
        results = [(260, 10.93, 12.7162, 15.7085, 90.0, 90.0, 90.0, 2183.3)]
        volume = vol_unitcell(*cell)
        atol, ltol, vol_threshold = more_results_parameters(volume)
        cells = self.structures.find_by_volume(volume, vol_threshold)
        self.assertEqual(cells, results)
        lattice1 = lattice.Lattice.from_parameters(*cell)
        for curr_cell in cells:
            try:
                lattice2 = lattice.Lattice.from_parameters(*curr_cell[1:7])
            except ValueError:
                continue
            mapping = lattice1.find_mapping(lattice2, ltol, atol, skip_rotation_matrix=True)
            if mapping:
                idlist.append(curr_cell[0])
        self.assertEqual(idlist, [260])
