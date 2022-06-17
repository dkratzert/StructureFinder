import unittest

from structurefinder.searcher import database_handler


class TestDatabase(unittest.TestCase):
    def setUp(self) -> None:
        dbfilename = 'tests/test-data/test_with_authors.sql'
        self.db = database_handler.StructureTable(dbfilename)

    def test_search_author_not_in_database(self):
        res = self.db.find_authors('foo')
        self.assertEqual((), res)

    def test_search_author_is_in_database(self):
        res = self.db.find_authors('takano')
        self.assertEqual((8,), res)

    def test_find_text_and_authors(self):
        res = self.db.find_text_and_authors('takano')
        self.assertEqual((8,), res)

    def test_find_text_and_authors_2(self):
        res = self.db.find_text_and_authors('res')
        self.assertEqual((224, 226, 163, 255, 10, 173, 144, 218, 222, 223), res)

    def test_text_search(self):
        by_strings = self.db.find_by_strings('NTD51a')
        self.assertEqual((225,), by_strings)
        # and also case insensitive:
        by_strings = self.db.find_by_strings('ntd51A')
        self.assertEqual((225,), by_strings)

    def test_find_by_it_number(self):
        self.assertEqual([27], self.db.find_by_it_number(1))
        self.assertEqual([10, 37, 136, 218], self.db.find_by_it_number(5))
        self.assertEqual([], self.db.find_by_it_number(500))

    def test_find_by_elements(self):
        self.assertEqual([69], self.db.find_by_elements(['S', 'Sn']))
        self.assertEqual([69, 181], self.db.find_by_elements(['Sn']))
        self.assertEqual([], self.db.find_by_elements(['Xe']))
        self.assertEqual([1, 53, 151, 164, 236],
                         self.db.find_by_elements(['C', 'H', 'O', 'N', 'Cl'], onlyincluded=True))
        self.assertEqual([1, 50, 53, 109, 127, 151, 164, 203, 236],
                         self.db.find_by_elements(['C', 'H', 'O', 'N', 'Cl'],
                                                  excluding=['Al', 'B', 'S', 'Si', 'Br', 'P'],
                                                  onlyincluded=False))

    def test_find_by_date(self):
        self.assertEqual([5, 4], self.db.find_by_date(start='2019-01-01', end='2021-05-09'))

    def test_find_by_rvalue(self):
        self.assertEqual([69, 125, 129, 242], self.db.find_by_rvalue(0.030))

    def find_biggest_cell(self):
        self.assertEqual((250, 48.48, 21.72, 10.74), self.db.find_biggest_cell())

    def test_get_largest_id(self):
        self.assertEqual(255, self.db.get_largest_id())

    def test_get_lastrowid(self):
        self.assertEqual(255, self.db.database.get_lastrowid())

    def test_db_version(self):
        self.assertEqual(0, self.db.get_database_version())

    def test_cif_export(self):
        self.assertEqual('SHELXL-2016/6', self.db.get_cif_export_data(220).get('_audit_creation_method'))
        self.assertEqual(127.03, self.db.get_cif_export_data(220).get('_cell_angle_alpha'))

    def test_find_by_ccdc_num(self):
        # The database contsaains 'CCDC 1431890'
        self.assertEqual([6], self.db.find_by_ccdc_num('1431890'))
        self.assertEqual([6], self.db.find_by_ccdc_num('CCDC 1431890'))

    def test_find_by_volume(self):
        result = [(13, 9.451, 17.881, 18.285, 90.0, 102.054, 90.0, 3021.9),
                  (245, 9.451, 17.881, 18.285, 90.0, 102.054, 90.0, 3021.9)]
        self.assertEqual(result, self.db.find_by_volume(3021.9, threshold=0.01))
        self.assertEqual((), self.db.find_by_volume(30021.9, threshold=0.01))

    def test_get_cell_by_id(self):
        self.assertEqual((7.9492, 8.9757, 11.3745, 106.974, 91.963, 103.456, 750.33), self.db.get_cell_by_id(2))

    def test_get_cells_as_list(self):
        self.assertEqual([(7.9492, 8.9757, 11.3745, 106.974, 91.963, 103.456, 750.33)],
                         self.db.get_cells_as_list([2]))
        self.assertEqual([(7.9492, 8.9757, 11.3745, 106.974, 91.963, 103.456, 750.33),
                          (10.36, 18.037, 25.764, 127.03, 129.81, 90.51, 2260.487670154818)],
                         self.db.get_cells_as_list([16, 2]))

    def test_joined_arglist(self):
        self.assertEqual(('?, ?, ?, ?, ?'), self.db.joined_arglist([1, 2, 3, 'abc', 'def']))

    def test_get_cell_as_dict(self):
        result_cell = self.db.get_cell_as_dict(2)
        result = {'Id'   : 2, 'StructureId': 2, 'a': 7.9492, 'b': 8.9757, 'c': 11.3745,
                  'alpha': 106.974,
                  'beta' : 91.963, 'gamma': 103.456, 'volume': 750.33}
        self.assertDictEqual(result, result_cell)

    def test_get_row_as_dict(self):
        self.assertEqual('SHELXL-97', self.db.get_row_as_dict(2).get('_audit_creation_method'))

    def test_get_calc_sumformula(self):
        sumf = self.db.get_calc_sum_formula(2)
        self.assertEqual(2, sumf.get('Id'))
        self.assertEqual(18.0, sumf.get('Elem_C'))
        self.assertEqual(None, sumf.get('Elem_Cl'))
        self.assertEqual(19.0, sumf.get('Elem_H'))
        self.assertEqual(1.0, sumf.get('Elem_N'))

    def test_get_atom_table(self):
        self.assertEqual(('O1', 'O', 0.32157, 0.42645, 0.40201, 0, 1.0), self.db.get_atoms_table(2)[0])
        self.assertEqual(('O1', 'O', 1.50889, 2.31252, 4.34699, 0, 1.0),
                         self.db.get_atoms_table(2, cartesian=True)[0])

    def test_get_filepath(self):
        self.assertEqual((b'p-1', b'C:/_DEV/GitHub/StructureFinder\\tests\\test-data\\106c.tar.bz2'),
                         self.db.get_filepath(2))


if __name__ == '__main__':
    unittest.main()
