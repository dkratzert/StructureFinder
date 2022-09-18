import unittest
from collections import namedtuple
from pathlib import Path

from structurefinder.searcher import database_handler
from structurefinder.strf_cmd import run_index


class TestDatabase(unittest.TestCase):
    def setUp(self) -> None:
        dbfilename = 'tests/test-data/test.sql'
        self.db = database_handler.StructureTable(dbfilename)

    def test_text_search(self):
        by_strings = self.db.find_by_strings('NTD51a')
        self.assertEqual((237,), by_strings)
        # and also case insensitive:
        by_strings = self.db.find_by_strings('ntd51A')
        self.assertEqual((237,), by_strings)

    def test_find_by_it_number(self):
        self.assertEqual([33], self.db.find_by_it_number(1))
        self.assertEqual([6, 14, 43, 142], self.db.find_by_it_number(5))
        self.assertEqual([], self.db.find_by_it_number(500))

    def test_find_by_elements(self):
        self.assertEqual([75], self.db.find_by_elements(['S', 'Sn']))
        self.assertEqual([75, 187], self.db.find_by_elements(['Sn']))
        self.assertEqual([], self.db.find_by_elements(['Xe']))
        self.assertEqual([15, 59, 157, 170, 260],
                         self.db.find_by_elements(['C', 'H', 'O', 'N', 'Cl'], onlyincluded=True))
        self.assertEqual([15, 56, 59, 115, 133, 157, 170, 209, 260],
                         self.db.find_by_elements(['C', 'H', 'O', 'N', 'Cl'],
                                                  excluding=['Al', 'B', 'S', 'Si', 'Br', 'P'],
                                                  onlyincluded=False))

    def test_find_by_date(self):
        self.assertEqual([16, 17, 20, 21, 241], self.db.find_by_date(start='2017-08-25', end='2018-05-05'))

    def test_find_by_rvalue(self):
        self.assertEqual([75, 131, 135, 243], self.db.find_by_rvalue(0.030))

    def find_biggest_cell(self):
        self.assertEqual((250, 48.48, 21.72, 10.74), self.db.find_biggest_cell())

    def test_get_largest_id(self):
        self.assertEqual(263, self.db.get_largest_id())

    def test_get_lastrowid(self):
        self.assertEqual(263, self.db.database.get_lastrowid())

    def test_db_version(self):
        self.assertEqual(0, self.db.get_database_version())

    def test_cif_export(self):
        self.assertEqual('SHELXL-2016/6', self.db.get_cif_export_data(1).get('_audit_creation_method'))
        self.assertEqual(127.03, self.db.get_cif_export_data(1).get('_cell_angle_alpha'))

    def test_find_by_ccdc_num(self):
        # The database contsaains 'CCDC 1431890'
        self.assertEqual([22], self.db.find_by_ccdc_num('1431890'))
        self.assertEqual([22], self.db.find_by_ccdc_num('CCDC 1431890'))

    def test_find_by_volume(self):
        result = [(9, 9.451, 17.881, 18.285, 90.0, 102.054, 90.0, 3021.9),
                  (252, 9.451, 17.881, 18.285, 90.0, 102.054, 90.0, 3021.9)]
        self.assertEqual(result, self.db.find_by_volume(3021.9, threshold=0.01))
        self.assertEqual((), self.db.find_by_volume(30021.9, threshold=0.01))

    def test_get_cell_by_id(self):
        self.assertEqual((7.9492, 8.9757, 11.3745, 106.974, 91.963, 103.456, 750.33), self.db.get_cell_by_id(16))

    def test_get_cells_as_list(self):
        self.assertEqual([(7.9492, 8.9757, 11.3745, 106.974, 91.963, 103.456, 750.33)],
                         self.db.get_cells_as_list([16]))
        self.assertEqual([(10.36, 18.037, 25.764, 127.03, 129.81, 90.51, 2260.487670154818),
                          (7.9492, 8.9757, 11.3745, 106.974, 91.963, 103.456, 750.33)],
                         self.db.get_cells_as_list([1, 16]))

    def test_joined_arglist(self):
        self.assertEqual(('?, ?, ?, ?, ?'), self.db.joined_arglist([1, 2, 3, 'abc', 'def']))

    def test_get_cell_as_dict(self):
        result_cell = self.db.get_cell_as_dict(16)
        result = {'Id'   : 16, 'StructureId': 16, 'a': 7.9492, 'b': 8.9757, 'c': 11.3745,
                  'alpha': 106.974,
                  'beta' : 91.963, 'gamma': 103.456, 'volume': 750.33}
        self.assertDictEqual(result, result_cell)

    def test_get_row_as_dict(self):
        self.assertEqual('SHELXL-97', self.db.get_row_as_dict(16).get('_audit_creation_method'))

    def test_get_calc_sumformula(self):
        sumf = self.db.get_calc_sum_formula(16)
        self.assertEqual(13, sumf.get('Id'))
        self.assertEqual(18.0, sumf.get('Elem_C'))
        self.assertEqual(None, sumf.get('Elem_Cl'))
        self.assertEqual(19.0, sumf.get('Elem_H'))
        self.assertEqual(1.0, sumf.get('Elem_N'))

    def test_get_atom_table(self):
        self.assertEqual(('O1', 'O', 0.32157, 0.42645, 0.40201, 0, 1.0), self.db.get_atoms_table(16)[0])
        self.assertEqual(('O1', 'O', 1.5088943989965458, 2.312523688689475, 4.346994224791996, 0, 1.0),
                         self.db.get_atoms_table(16, cartesian=True)[0])

    def test_get_filepath(self):
        self.assertEqual((b'p-1', b'/Users/daniel/GitHub/StructureFinder/test-data/106c.tgz'),
                         self.db.get_filepath(16))


class TestMerging(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = 'tests/merge_test'
        self.tearDown()
        Path(self.test_dir).mkdir(exist_ok=True)
        Args = namedtuple('Args', 'dir, outfile, fillcif, fillres, delete, ex')
        args1 = Args(dir=['tests/test-data/051a'], outfile=f'{self.test_dir}/db1.sqlite', fillcif=True, fillres=True,
                     delete=True, ex='')
        args2 = Args(dir=['tests/test-data/106c'], outfile=f'{self.test_dir}/db2.sqlite', fillcif=True, fillres=True,
                     delete=True, ex='')
        run_index(args1)
        run_index(args2)
        self.db1 = database_handler.StructureTable(f'{self.test_dir}/db1.sqlite')
        self.db2 = database_handler.StructureTable(f'{self.test_dir}/db2.sqlite')

    def tearDown(self) -> None:
        try:
            Path(self.test_dir).joinpath(Path('db1.sqlite')).unlink(missing_ok=True)
            Path(self.test_dir).joinpath(Path('db2.sqlite')).unlink(missing_ok=True)
            Path(self.test_dir).rmdir()
        except PermissionError:
            print('\nUnable to delete all test files (db1.sqlite, db2.sqlite).')

    def test_number_of_entries(self):
        self.assertEqual(2, len(self.db1))
        self.assertEqual(2, len(self.db2))

    def test_merge_number_of_entries(self):
        self.db1.database.merge_databases(self.db2.dbfilename)
        self.assertEqual(4, self.db1.database.get_lastrowid())
        self.assertEqual(2, self.db2.database.get_lastrowid())

    def test_merge_ids(self):
        self.db1.database.merge_databases(self.db2.dbfilename)
        self.assertEqual([1, 2, 3, 4], [x[0] for x in self.db1.get_all_structure_names()])

    def test_merge_cell_ids(self):
        self.db1.database.merge_databases(self.db2.dbfilename)
        self.assertEqual((10.6456, 11.033, 19.9214, 90.0, 98.938, 90.0, 2311.4138821278034), self.db1.get_cell_by_id(1))
        # The third id of db1 has the same id
        self.assertEqual((7.9492, 8.9757, 11.3745, 106.974, 91.963, 103.456, 750.3353530415042),
                         self.db1.get_cell_by_id(3))
        # as the first row of db2, because db2 is merged into db1
        self.assertEqual((7.9492, 8.9757, 11.3745, 106.974, 91.963, 103.456, 750.3353530415042),
                         self.db2.get_cell_by_id(1))

    def test_merge_atoms(self):
        self.db1.database.merge_databases(self.db2.dbfilename)
        self.assertListEqual(self.db2.get_atoms_table(1), self.db1.get_atoms_table(3))
        self.assertListEqual(self.db2.get_atoms_table(2), self.db1.get_atoms_table(4))


if __name__ == '__main__':
    unittest.main()
