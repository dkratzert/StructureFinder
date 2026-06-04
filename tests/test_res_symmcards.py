"""
Tests that SYMM cards from .res files are correctly stored in the database
and can be used to grow molecules.

Regression test for bug where `to_fractional()` / `toShelxl()` (non-existent
camelCase methods) were called on SymmetryElement objects, silently failing and
leaving _space_group_symop_operation_xyz empty in the database, causing:
  "Cif file has no symmcards, unable to grow structure."
"""
import unittest
import uuid
from collections import namedtuple
from pathlib import Path

from fastmolwidget.sdm import SDM

from structurefinder.searcher import database_handler
from structurefinder.strf_cmd import run_index


Args = namedtuple('Args', 'dir, outfile, fillcif, fillres, delete, ex, no_archive')


class TestResSymmcards(unittest.TestCase):
    """Index a centrosymmetric P-31c .res file and verify symmcards are stored."""

    def setUp(self):
        self.test_dir = 'tests/tmp_symmcards'
        self.db_file = str(uuid.uuid4()) + '.sqlite'
        Path(self.test_dir).mkdir(exist_ok=True)
        args = Args(
            dir=['tests/test-data'],
            outfile=f'{self.test_dir}/{self.db_file}',
            fillcif=False,
            fillres=True,
            delete=True,
            ex='',
            no_archive=False,
        )
        run_index(args)
        self.db = database_handler.StructureTable(f'{self.test_dir}/{self.db_file}')
        # Find the p-31c entry by filename
        rows = self.db.get_structure_rows_by_ids()
        self.p31c_id = None
        for row in rows:
            filename = row[2]
            if isinstance(filename, bytes):
                filename = filename.decode()
            if 'p-31c' in filename:
                self.p31c_id = row[0]
                break

    def tearDown(self):
        del self.db
        for f in Path(self.test_dir).glob('*'):
            f.unlink(missing_ok=True)
        Path(self.test_dir).rmdir()

    def test_p31c_entry_found(self):
        """The p-31c.res file must be indexed into the database."""
        self.assertIsNotNone(self.p31c_id, 'p-31c.res entry not found in database')

    def test_symmcards_not_empty(self):
        """_space_group_symop_operation_xyz must be non-empty after indexing a .res file."""
        row = self.db.get_row_as_dict(self.p31c_id)
        symm_xyz = row.get('_space_group_symop_operation_xyz') or ''
        self.assertNotEqual('', symm_xyz,
                            '_space_group_symop_operation_xyz is empty — to_cif() not called correctly')

    def test_symmcards_contain_identity(self):
        """The identity operation x,y,z must be present."""
        row = self.db.get_row_as_dict(self.p31c_id)
        symm_xyz = row.get('_space_group_symop_operation_xyz') or ''
        # After space-stripping (as done in view_molecule) the identity becomes +x,+y,+z
        stripped = symm_xyz.replace("'", "").replace(" ", "")
        self.assertIn('+x,+y,+z', stripped)

    def test_symmcards_count(self):
        """P-31c has 5 SYMM cards plus the identity = 6 operations stored."""
        row = self.db.get_row_as_dict(self.p31c_id)
        symm_xyz = (row.get('_space_group_symop_operation_xyz') or '').strip()
        ops = [line for line in symm_xyz.splitlines() if line.strip()]
        self.assertEqual(6, len(ops),
                         f'Expected 6 symmetry operations, got {len(ops)}: {ops}')

    def test_view_molecule_symmcard_parsing(self):
        """Simulate exactly what view_molecule does: split must yield non-empty first element."""
        row = self.db.get_row_as_dict(self.p31c_id)
        symm_xyz = row.get('_space_group_symop_operation_xyz') or ''
        symmcards = symm_xyz.replace("'", "").replace(" ", "").split("\n")
        self.assertNotEqual('', symmcards[0],
                            'view_molecule would print "no symmcards" and abort growing')

    def test_sdm_grows_without_error(self):
        """SDM must be constructable and calc_sdm must run without error."""
        cell = self.db.get_cell_by_id(self.p31c_id)
        self.assertIsNotNone(cell)
        row = self.db.get_row_as_dict(self.p31c_id)
        symm_xyz = row.get('_space_group_symop_operation_xyz') or ''
        symmcards = symm_xyz.replace("'", "").replace(" ", "").split("\n")
        atoms = self.db.get_atoms_table(self.p31c_id, cartesian=False, as_list=True)
        self.assertTrue(atoms, 'No atoms found for p-31c entry')
        sdm = SDM(atoms, symmcards, cell)
        needsymm = sdm.calc_sdm()
        grown = sdm.packer(sdm, needsymm)
        # The grown structure must contain at least as many atoms as the asymmetric unit
        self.assertGreaterEqual(len(grown), len(atoms))


class TestP21cSymmcards(unittest.TestCase):
    """Index the existing P 2(1)/c test file to ensure it still works correctly."""

    def setUp(self):
        self.test_dir = 'tests/tmp_symmcards_p21c'
        self.db_file = str(uuid.uuid4()) + '.sqlite'
        Path(self.test_dir).mkdir(exist_ok=True)
        args = Args(
            dir=['tests/test-data'],
            outfile=f'{self.test_dir}/{self.db_file}',
            fillcif=False,
            fillres=True,
            delete=True,
            ex='',
            no_archive=False,
        )
        run_index(args)
        self.db = database_handler.StructureTable(f'{self.test_dir}/{self.db_file}')
        rows = self.db.get_structure_rows_by_ids()
        self.p21c_id = None
        for row in rows:
            filename = row[2]
            if isinstance(filename, bytes):
                filename = filename.decode()
            if filename == 'p21c.res':
                self.p21c_id = row[0]
                break

    def tearDown(self):
        del self.db
        for f in Path(self.test_dir).glob('*'):
            f.unlink(missing_ok=True)
        Path(self.test_dir).rmdir()

    def test_p21c_symmcards_not_empty(self):
        """P 2(1)/c has one SYMM card plus identity, must be stored."""
        self.assertIsNotNone(self.p21c_id)
        row = self.db.get_row_as_dict(self.p21c_id)
        symm_xyz = row.get('_space_group_symop_operation_xyz') or ''
        self.assertNotEqual('', symm_xyz)

    def test_p21c_symmcards_count(self):
        """P 2(1)/c: ShelXFile expands LATT 1 (centrosymmetric) into 4 full operations:
        identity, inversion, SYMM card, and SYMM+inversion."""
        row = self.db.get_row_as_dict(self.p21c_id)
        symm_xyz = (row.get('_space_group_symop_operation_xyz') or '').strip()
        ops = [line for line in symm_xyz.splitlines() if line.strip()]
        self.assertEqual(4, len(ops), f'Expected 4 ops, got {len(ops)}: {ops}')


if __name__ == '__main__':
    unittest.main()


