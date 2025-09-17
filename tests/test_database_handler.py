import unittest
import uuid
from collections import namedtuple
from pathlib import Path

from structurefinder.searcher import database_handler
from structurefinder.strf_cmd import run_index


class TestDatabase(unittest.TestCase):
    def setUp(self) -> None:
        dbfilename = 'tests/test-data/test.sql'
        database_handler.columns.reset_defaults()
        self.db = database_handler.StructureTable(dbfilename)

    def test_column(self):
        c = database_handler.Column(name='foo', table='Structure', visible=True)
        # This is initialized after all other columns, therefore 43:
        assert c.position == 43

    def test_column_sources(self):
        columns = database_handler.columns
        columns.reset_defaults()
        assert columns.current_columns() == (
            'Structure.dataname, Structure.filename, Residuals.modification_time, '
            'Structure.path')
        assert columns.visible_headers() == ['dataname', 'filename', 'modification_time', 'path']
        assert columns.visible_header_names() == ['Id', 'Data Name', 'File Name', 'Last Modified', 'Path']
        assert columns.default_columns() == ['dataname', 'filename', 'modification_time', 'path']

    def test_get_structure_rows_by_ids_without_id(self):
        rows = self.db.get_structure_rows_by_ids()
        assert len(rows) == 263
        assert rows[0] == (1,
                           b'hubert',
                           b'hubert2.cif',
                           '2017-08-15',
                           b'/Users/daniel/GitHub/StructureFinder/test-data')

    def test_get_structure_rows_by_ids_with_id(self):
        rows = self.db.get_structure_rows_by_ids([1, 3])
        assert len(rows) == 2
        assert rows[0] == (1,
                           b'hubert',
                           b'hubert2.cif',
                           '2017-08-15',
                           b'/Users/daniel/GitHub/StructureFinder/test-data')

    def test_get_structure_rows_by_ids_with_columns_set(self):
        database_handler.columns._cell_formula_units_Z.visible = True
        database_handler.columns._cell_formula_units_Z.position = 1
        database_handler.columns._chemical_formula_sum.visible = True
        database_handler.columns._chemical_formula_sum.position = 2
        database_handler.columns._exptl_crystal_colour.visible = True
        database_handler.columns._exptl_crystal_colour.position = 3
        database_handler.columns._chemical_formula_weight.visible = True
        database_handler.columns._chemical_formula_weight.position = 4
        database_handler.columns._space_group_IT_number.visible = True
        database_handler.columns._space_group_IT_number.position = 5
        database_handler.columns._space_group_name_H_M_alt.visible = True
        database_handler.columns.dataname.visible = False
        database_handler.columns.filename.visible = False
        database_handler.columns.path.visible = False
        # database_handler.columns.file_size.visible = False
        database_handler.columns.modification_time.visible = False

        rows = self.db.get_structure_rows_by_ids([23])
        assert rows[0] == (23,
                           4,
                           'C3 H9 Br0.962 Cd Cl2.038 O S',
                           'colourless', '354.7', 62, 'P n m a')

    def test_get_structure_rows_by_ids_with_columns_from_both_set(self):
        database_handler.columns._chemical_formula_sum.visible = True
        database_handler.columns._chemical_formula_sum.position = 1
        database_handler.columns.dataname.visible = True
        database_handler.columns.dataname.position = 2
        database_handler.columns.filename.visible = False
        database_handler.columns.modification_time.visible = False
        database_handler.columns.path.visible = False
        rows = self.db.get_structure_rows_by_ids([23])
        assert rows[0] == (23, 'C3 H9 Br0.962 Cd Cl2.038 O S', b'2004800')

    def test_text_search(self):
        by_strings = self.db.find_by_strings('NTD51a')
        self.assertEqual((237,), by_strings)
        # and also case-insensitive:
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
        self.db1_file = str(uuid.uuid4()) + '.sqlite'
        self.db2_file = str(uuid.uuid4()) + '.sqlite'
        Path(self.test_dir).mkdir(exist_ok=True)
        Args = namedtuple('Args', 'dir, outfile, fillcif, fillres, delete, ex, no_archive')
        args1 = Args(dir=['tests/test-data/051a'], outfile=f'{self.test_dir}/{self.db1_file}', fillcif=True,
                     fillres=True,
                     delete=True, ex='', no_archive=False)
        args2 = Args(dir=['tests/test-data/106c'], outfile=f'{self.test_dir}/{self.db2_file}', fillcif=True,
                     fillres=True,
                     delete=True, ex='', no_archive=False)
        run_index(args1)
        run_index(args2)
        self.db1 = database_handler.StructureTable(f'{self.test_dir}/{self.db1_file}')
        self.db2 = database_handler.StructureTable(f'{self.test_dir}/{self.db2_file}')

    def tearDown(self) -> None:
        del self.db1
        del self.db2
        Path(self.test_dir).joinpath(Path(self.db1_file)).unlink(missing_ok=True)
        Path(self.test_dir).joinpath(Path(self.db2_file)).unlink(missing_ok=True)
        [x.unlink() for x in Path(self.test_dir).glob('*.*')]
        Path(self.test_dir).rmdir()

    def test_number_of_entries(self):
        self.assertEqual(2, len(self.db1))
        self.assertEqual(2, len(self.db2))

    def test_merge_number_of_entries(self):
        self.db1.database.merge_databases(self.db2.dbfilename)
        self.assertEqual(4, self.db1.database.get_lastrowid())
        self.assertEqual(2, self.db2.database.get_lastrowid())

    def test_merge_ids(self):
        self.db1.database.merge_databases(self.db2.dbfilename)
        self.assertEqual([1, 2, 3, 4], [x[0] for x in self.db1.get_structure_rows_by_ids()])

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

    def test_merge_residuals_with_empty_authors_table(self):
        # Previous versions failed if the authors table was empty
        self.maxDiff = None
        self.db2.database.db_request("DELETE FROM authors")
        self.db2.database.commit_db()
        self.db1.database.merge_databases(self.db2.dbfilename)
        db2_row1 = self.db2.get_row_as_dict(1)
        self.assertEqual(1, db2_row1.get('Id'))
        self.assertEqual(1, db2_row1.get('StructureId'))

    def test_merge_residuals(self):
        self.maxDiff = None
        self.db1.database.merge_databases(self.db2.dbfilename)
        db2_row1 = self.db2.get_row_as_dict(1)
        self.assertEqual(1, db2_row1.get('Id'))
        self.assertEqual(1, db2_row1.get('StructureId'))
        db2_row1.pop('Id')
        db2_row1.pop('StructureId')
        db1_row3 = self.db1.get_row_as_dict(3)
        self.assertEqual(2, db1_row3.get('Id'))
        self.assertEqual(3, db1_row3.get('StructureId'))
        db1_row3.pop('Id')
        db1_row3.pop('StructureId')
        self.assertDictEqual(db2_row1, db1_row3)
        db2_row2 = self.db2.get_row_as_dict(2)
        db2_row2.pop('Id')
        db2_row2.pop('StructureId')
        db1_row4 = self.db1.get_row_as_dict(4)
        db1_row4.pop('Id')
        db1_row4.pop('StructureId')
        self.assertDictEqual(db2_row2, db1_row4)


def test_string_type():
    assert database_handler.string_type('foo') == 'foo'
    assert database_handler.string_type(5) == '5'
    assert database_handler.string_type(5.8) == '5.8'
    assert database_handler.string_type(b'5.8') == '5.8'


def test_float_type():
    assert database_handler.float_type(1) == 1.0
    assert database_handler.float_type(1.5) == 1.5
    assert database_handler.float_type('1') == 1.0
    assert database_handler.float_type(b'1') == 1.0


def test_size_repr():
    # Not convertible to int:
    assert database_handler.size_repr('foo') == 'foo'
    assert database_handler.size_repr(12344325) == '11.77'
    assert database_handler.size_repr('12344325') == '11.77'
    assert database_handler.size_repr(b'12344325') == '11.77'
    assert database_handler.size_repr(b'12344325') == '11.77'


def test_ccdc_repr():
    assert database_handler.ccdc_repr('CCDC 21341324') == '21341324'
    assert database_handler.ccdc_repr('21341324') == '21341324'
    assert database_handler.ccdc_repr(b'21341324') == '21341324'


def test_default_repr():
    assert database_handler.default_repr('foo') == 'foo'
    assert database_handler.default_repr('123.678') == '123.678'
    assert database_handler.default_repr(b'123.678') == '123.678'


if __name__ == '__main__':
    unittest.main()
