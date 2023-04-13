from itertools import chain
from math import log
from pathlib import Path
from typing import Optional, List, Tuple

import sqlalchemy as sa
from PyQt5 import QtCore
from sqlalchemy.orm import sessionmaker, Session

from structurefinder.db.mapping import Structure, Residuals, Cell, Base
from structurefinder.pymatgen.core import lattice
from structurefinder.searcher import misc
from structurefinder.searcher.misc import more_results_parameters, regular_results_parameters
from structurefinder.shelxfile.elements import sorted_atoms


def table_exists(table: str, engine: sa.Engine, schema=None):
    inspector = sa.inspect(engine)
    return inspector.has_table(table, schema)


class DB(QtCore.QObject):
    progress = QtCore.pyqtSignal((int, int))

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.engine = None
        self.session: Optional[Session] = None
        self.Session: Optional[sessionmaker] = None
        self.structure_id: Optional[int] = None
        self.structure: Optional[Structure] = None

    def load_database(self, database_file: Path):
        database_path = database_file.resolve()
        url_object = sa.URL.create("sqlite", database=str(database_path))
        self.engine = sa.create_engine(url_object, echo=False)
        if not database_path.exists():
            Base.metadata.create_all(self.engine)
        self.Session: sessionmaker = sessionmaker(self.engine)

    def set_structure(self, session, structureId: int) -> None:
        stmt = sa.select(Structure).filter_by(Id=structureId)
        self.structure = session.scalar(stmt)

    def structure_count(self) -> int:
        with self.Session() as session:
            num = session.query(Structure).count()
        return num

    def get_lastrowid(self):
        return self.structure_count()

    def get_all_structures(self, idlist: List[int] = None) -> List[sa.Row]:
        """
        sqlalchemy.engine.Engine SELECT "Structure"."Id", "Structure".dataname, "Structure".filename,
        "Residuals".modification_time, "Structure".path
        FROM "Structure" JOIN "Residuals" ON "Structure"."Id" = "Residuals"."StructureId"
        """
        with self.engine.connect() as conn:
            stmt = (sa.select(Structure.Id, Structure.dataname, Structure.filename,
                              Residuals.modification_time, Structure.path)
                    .join_from(Structure, Residuals)
                    )
            if idlist:
                stmt = stmt.where(Structure.Id.in_(idlist))
            return conn.execute(stmt).tuples().all()

    def _find_by_volume(self, volume: float, threshold: float = 0) -> List[sa.Row]:
        """
        Searches cells with volume between upper and lower limit. Returns the Id and the unit cell.
        :param threshold: Volume uncertaincy where to search
        :param volume: the unit cell volume
        """
        if not threshold:
            threshold = log(volume) + 1.2
        upper_limit = float(volume + threshold)
        lower_limit = float(volume - threshold)
        stmt = (
            sa.select(Structure.Id, Structure.dataname, Structure.filename, Residuals.modification_time, Structure.path,
                      Cell.a, Cell.b, Cell.c, Cell.alpha, Cell.beta, Cell.gamma, Cell.volume
                      )
            .join_from(Structure, Residuals)
            .join_from(Structure, Cell)
            .filter(sa.between(Cell.volume, lower_limit, upper_limit))
        )
        with self.engine.connect() as conn:
            return list(conn.execute(stmt).tuples())

    def search_cell(self, cell: list, more_results: bool = False, sublattice: bool = False) -> List[sa.Row]:
        """
        Searches for a unit cell and resturns a list of found structures for main table.
        This method does not validate the cell. This has to be done before!
        """
        try:
            volume = misc.vol_unitcell(*cell)
            if volume < 0:
                return []
        except ValueError:
            return []
        if more_results:
            # more results:
            print('more results activated')
            atol, ltol, vol_threshold = more_results_parameters(volume)
        else:
            # regular:
            atol, ltol, vol_threshold = regular_results_parameters(volume)
        try:
            # the fist number in the result is the structureid:
            cells = self._find_by_volume(volume, vol_threshold)
            if sublattice:
                # sub- and superlattices:
                for v in [volume * x for x in [2.0, 3.0, 4.0, 6.0, 8.0, 10.0]]:
                    # First a list of structures where the volume is similar:
                    cells.extend(self._find_by_volume(v, vol_threshold))
                cells = list(set(cells))
        except (ValueError, AttributeError):
            return []
        # Real lattice comparing in G6:
        results = []
        num_cells = len(cells)
        print(f'{num_cells} cells to check at {vol_threshold:.2f} A^3 threshold.')
        if cells:
            lattice1 = lattice.Lattice.from_parameters(*cell)
            for num, curr_cell in enumerate(cells):
                self.progress.emit(num, num_cells)
                try:
                    lattice2 = lattice.Lattice.from_parameters(curr_cell.a, curr_cell.b, curr_cell.c,
                                                               curr_cell.alpha, curr_cell.beta, curr_cell.gamma)
                except ValueError:
                    continue
                mapping = lattice1.find_mapping(lattice2, ltol, atol, skip_rotation_matrix=True)
                if mapping:
                    results.append(curr_cell)
        return results

    def find_text_and_authors(self, txt: str) -> Tuple[Tuple, ...]:
        result_txt = self.find_authors(txt)
        result_authors = self.find_by_strings(txt)
        result_txt = set(result_txt)
        result_txt.update(result_authors)
        return tuple(result_txt)

    def find_by_ccdc_num(self, ccdc: str) -> Tuple:
        """
        Find structures with respective CCDC number.
        """

        stmt = sa.select(
            Residuals.StructureId
        ).filter_by(_database_code_depnum_ccdc_archive=ccdc)
        with self.engine.connect() as conn:
            return self.flatten(conn, stmt)

    def find_by_date(self, start='0000-01-01', end='NOW') -> tuple[int, ...]:
        """
        Find structures between start and end date.
        """
        stmt = sa.select(Residuals.StructureId).where(sa.between(Residuals.modification_time, start, end))
        with self.engine.connect() as conn:
            return self.flatten(conn, stmt)

    def find_by_rvalue(self, rvalue: float) -> tuple[int, ...]:
        """
        Finds structures with R1 value better than rvalue. I search both R1 values, because often one or even both
        are missing.
        """
        stmt = sa.select(Residuals.StructureId).where((Residuals._refine_ls_R_factor_gt <= rvalue) |
                                                      (Residuals._refine_ls_R_factor_all <= rvalue))
        with self.engine.connect() as conn:
            return self.flatten(conn, stmt)

    def find_by_it_number(self, number: int) -> Tuple[int, ...]:
        """
        Find structures by space group number in international tables of
        crystallography.
        Returns a list of index numbers.
        """
        try:
            value = int(number)
        except ValueError:
            return tuple()
        stmt = sa.select(Residuals.StructureId).filter_by(_space_group_IT_number=value)
        with self.engine.connect() as conn:
            return self.flatten(conn, stmt)

    def find_by_strings(self, text: str) -> Tuple:
        """
        Searches cells with volume between upper and lower limit
        :param text: Volume uncertaincy where to search
        id, name, data, path
        """
        req = sa.text('''SELECT StructureId FROM txtsearch 
                    WHERE filename MATCH :text 
                        OR dataname MATCH :text
                        OR path MATCH :text
                        OR shelx_res_file MATCH :text
               ''')
        with self.engine.connect() as conn:
            args = {'text': text}
            return self.flatten(conn, req, args)

    def flatten(self, conn, stmt, args=None):
        return tuple(chain(*conn.execute(stmt, args)))

    def find_authors(self, text: str) -> Tuple:
        if not table_exists(table='authortxtsearch', engine=self.engine):
            return tuple()
        search = f"{'*'}{text}{'*'}"
        select = """SELECT StructureId from authortxtsearch """
        req = sa.text(f'''
            {select}
                WHERE _audit_author_name MATCH :text 
                UNION
            {select}
                WHERE _audit_contact_author_name MATCH :text
                UNION
            {select}
                WHERE _publ_contact_author_name MATCH :text
                UNION
            {select}
                WHERE _publ_contact_author MATCH :text
                UNION
            {select}
                WHERE _publ_author_name MATCH :text
        ''')
        with self.engine.connect() as conn:
            result = conn.execute(req, {'text': search}).all()
        return tuple(chain(*result))

    def find_by_elements(self, formula: str, formula_ex: str = '', onlyincluded: bool = False) -> tuple[int, ...]:
        """
        Find structures where certain elements are included in the sum formula.
        """
        elements = misc.get_list_of_elements(formula)
        if elements is None:
            return ()
        excluding = misc.get_list_of_elements(formula_ex)
        if excluding is None:
            return ()
        # Find all structures where these elements are included:
        el = ' NOT NULL AND '.join(['Elem_' + x.capitalize() for x in elements]) + ' NOT NULL '
        # Find all structures where these elements are included and the others not included:
        exclude = ' IS NULL AND '.join(['Elem_' + x.capitalize() for x in excluding]) + ' IS NULL '
        if not excluding:
            req = '''SELECT StructureId from sum_formula WHERE ({}) '''.format(el)
        else:
            # With exclude condition
            if elements:
                req = '''SELECT StructureId from sum_formula WHERE ({} AND {}) '''.format(el, exclude)
            else:
                req = '''SELECT StructureId from sum_formula WHERE ({}) '''.format(exclude)
        if onlyincluded:
            elex = list(set(sorted_atoms) - set(elements))
            exclude = ' IS NULL AND '.join(['Elem_' + x.capitalize() for x in elex]) + ' IS NULL '
            req = '''SELECT StructureId from sum_formula WHERE ({} AND {}) '''.format(el, exclude)
        with self.engine.connect() as conn:
            return tuple(chain(*conn.execute(sa.text(req))))


if __name__ == '__main__':
    db = DB()
    db.load_database(Path('./test.sqlite'))
    """print(db.search_cell(cell=[12.955, 12.955, 12.955, 90.0, 90.0, 90.0],
                         # sublattice=True,
                         # more_results=True
                         ))"""
    # print(db.find_by_elements('C6H1O1Ag', formula_ex=''))
    # volume = db._find_by_volume(500)
    # print(db.find_by_ccdc_num('1979688'))
    #print(db.find_by_rvalue(0.02))
    with db.Session() as session:
        print(db.structure_count())
