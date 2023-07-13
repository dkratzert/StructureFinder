# -*- coding: utf-8 -*-
"""
Created on 09.02.2015

 ----------------------------------------------------------------------------
* "THE BEER-WARE LICENSE" (Revision 42):
* <dkratzert@gmx.de> wrote this file. As long as you retain this
* notice you can do whatever you want with this stuff. If we meet some day, and
* you think this stuff is worth it, you can buy me a beer in return.
* ----------------------------------------------------------------------------

@author: daniel


from PyQt5.QtSql import QSqlQuery, QSqlDatabase

con = QSqlDatabase.addDatabase("QSQLITE")
con.setDatabaseName("/Users/daniel/Documents/GitHub/StructureFinder/structuredb.sqlite")

query = QSqlQuery()
query.exec('''SELECT Name, element, x, y, z FROM ATOMS''')
while query.next():
    results.append(query.value(0), query.value(1), query.value(2), query.value(3), query.value(4))
query.finish()

con.close()
con.isOpen()
- False
QSqlDatabase::removeDatabase("sales")
"""
import sys
from math import log
from sqlite3 import OperationalError, ProgrammingError, connect, InterfaceError
from typing import List, Union, Tuple, Dict, Optional

from structurefinder.searcher.fileparser import CifFile
from structurefinder.shelxfile.elements import sorted_atoms

DEBUG = False

__metaclass__ = type  # use new-style classes

# db_enoding = 'ISO-8859-15'
db_enoding = 'utf-8'


class DatabaseRequest():
    def __init__(self, dbfile):
        """
        creates a connection and the cursor to the SQLite3 database file "dbfile".
        :param dbfile: database file
        :type dbfile: str
        """
        # open the database
        self.id_translate_table: Optional[Dict[int, int]] = None
        self.dbfile = dbfile
        self.con = connect(dbfile, check_same_thread=False)
        self.con.execute("PRAGMA foreign_keys = ON")
        ## These make requests faster: ###
        self.con.execute("PRAGMA main.journal_mode = MEMORY;")
        self.con.execute("PRAGMA temp.journal_mode = MEMORY;")
        self.con.execute("PRAGMA main.cache_size = -20000;")
        self.con.execute("PRAGMA recursive_triggers = 1;")
        self.con.execute("PRAGMA main.synchronous = 0;")
        self.con.execute("PRAGMA threads = 2;")
        # self.con.text_factory = str
        # self.con.text_factory = bytes
        with self.con:
            # set the database cursor
            self.cur = self.con.cursor()

    def merge_databases(self, db2: str) -> None:
        """
        Merges db2 into the current database.
        """
        tables = ('Structure', 'Residuals', 'cell', 'atoms', 'sum_formula', 'authors')
        self.id_translate_table = dict()
        print(f'Old database size: {self.get_lastrowid()} structures.')
        self.con.execute(f"ATTACH '{db2}' as dba")
        self.con.execute("BEGIN")
        for table in tables:
            print(f'Merging table: {table}')
            try:
                self.merge_table(table)
            except OperationalError:
                print(f'\nMerging of table {table} failed!! Resulting database may be damaged!\n')
        self.con.commit()
        self.con.execute("detach database dba")
        self.init_textsearch()
        self.populate_fulltext_search_table()
        self.init_author_search()
        self.populate_author_fulltext_search()
        self.make_indexes()
        self.con.commit()
        print(f'\nMerging databases finished.\n'
              f'Database {self.dbfile} contains {self.get_lastrowid()} structures now.')

    def merge_table(self, table_name: str) -> None:
        # noinspection SqlResolve
        fetchone = self.con.execute(f"SELECT * from dba.{table_name}").fetchone()
        if not fetchone:
            print(f"Table is empty, skipping table '{table_name}'")
            return
        table_size = len(fetchone)
        placeholders = ', '.join('?' * table_size)
        last_row_id = self.db_fetchone(f"""SELECT max(id) FROM {table_name}""")[0]
        next_id = last_row_id + 1
        # noinspection SqlResolve
        for row in self.con.execute(f"select * FROM dba.{table_name}"):
            if table_name != 'Structure':
                # row[1] is the structure(id)
                self.con.execute(f"INSERT INTO {table_name} VALUES ({placeholders})",
                                 (next_id, self.id_translate_table[row[1]], *row[2:]))
            else:
                self.id_translate_table[row[0]] = next_id
                self.con.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", (next_id, *row[1:]))
            next_id += 1
            if next_id % 500 == 0:
                self.con.commit()
        self.con.commit()

    def initialize_db(self):
        """
        initializtes the db
        """

        # Format: 1 == APEX
        self.cur.execute('''
                    CREATE TABLE IF NOT EXISTS database_format (
                        Id                  INTEGER NOT NULL,
                        Format              INTEGER,              
                        PRIMARY KEY(Id));
                    ''')

        self.cur.execute('''
                    CREATE TABLE IF NOT EXISTS measurement (
                        Id    INTEGER NOT NULL,
                        name    VARCHAR(255),
                        PRIMARY KEY(Id));
                    ''')

        self.cur.execute('''
                    CREATE TABLE IF NOT EXISTS Structure (
                        Id    INTEGER NOT NULL,
                        measurement INTEGER NOT NULL,
                        path          TEXT,
                        filename      TEXT,
                        dataname      TEXT,
                        PRIMARY KEY(Id),
                          FOREIGN KEY(measurement)
                            REFERENCES Structure(Id)
                              ON DELETE CASCADE
                              ON UPDATE NO ACTION);
                    ''')

        self.cur.execute('''
                    CREATE TABLE IF NOT EXISTS Atoms (
                        Id    INTEGER NOT NULL,
                        StructureId    INTEGER NOT NULL,
                        Name       TEXT,
                        element    TEXT,
                        x          REAL,
                        y          REAL,
                        z          REAL,
                        occupancy  REAL,
                        part       INTEGER,
                        xc         REAL,
                        yc         REAL,
                        zc         REAL,
                    PRIMARY KEY(Id),
                      FOREIGN KEY(StructureId)
                        REFERENCES Structure(Id)
                          ON DELETE CASCADE
                          ON UPDATE NO ACTION);
                    ''')

        self.cur.execute('''
                    CREATE TABLE IF NOT EXISTS Residuals (
                        Id                                      INTEGER NOT NULL,
                        StructureId                             INTEGER NOT NULL,
                        _cell_formula_units_Z                   INTEGER,
                        _space_group_name_H_M_alt               TEXT,
                        _space_group_name_Hall                  TEXT,
                        _space_group_centring_type              TEXT,
                        _space_group_IT_number                  INTEGER,
                        _space_group_crystal_system             TEXT,
                        _space_group_symop_operation_xyz        TEXT,
                        _audit_creation_method                  TEXT,
                        _chemical_formula_sum                   TEXT,
                        _chemical_formula_weight                TEXT,
                        _exptl_crystal_description              TEXT,
                        _exptl_crystal_colour                   TEXT,
                        _exptl_crystal_size_max                 REAL,
                        _exptl_crystal_size_mid 		    	REAL,
                        _exptl_crystal_size_min 				REAL,
                        _exptl_absorpt_coefficient_mu 			REAL,
                        _exptl_absorpt_correction_type			TEXT,
                        _diffrn_ambient_temperature 			REAL,
                        _diffrn_radiation_wavelength 			REAL,
                        _diffrn_radiation_type 					TEXT,
                        _diffrn_source 							TEXT,
                        _diffrn_measurement_device_type 		TEXT,
                        _diffrn_reflns_number 					INTEGER,
                        _diffrn_reflns_av_R_equivalents 		INTEGER,
                        _diffrn_reflns_theta_min 				REAL,
                        _diffrn_reflns_theta_max 				REAL,
                        _diffrn_reflns_theta_full 				REAL,
                        _diffrn_measured_fraction_theta_max 	REAL,
                        _diffrn_measured_fraction_theta_full 	REAL,
                        _reflns_number_total 					INTEGER,
                        _reflns_number_gt 					    INTEGER,
                        _reflns_threshold_expression 			TEXT,
                        _reflns_Friedel_coverage 				REAL,
                        _computing_structure_solution 			TEXT,
                        _computing_structure_refinement 		TEXT,
                        _refine_special_details 				TEXT,
                        _refine_ls_abs_structure_Flack          TEXT,
                        _refine_ls_structure_factor_coef 		TEXT,
                        _refine_ls_weighting_details 			TEXT,
                        _refine_ls_number_reflns 				INTEGER,
                        _refine_ls_number_parameters 			INTEGER,
                        _refine_ls_number_restraints 			INTEGER,
                        _refine_ls_R_factor_all 				REAL,
                        _refine_ls_R_factor_gt             		REAL,
                        _refine_ls_wR_factor_ref       			REAL,
                        _refine_ls_wR_factor_gt         		REAL,
                        _refine_ls_goodness_of_fit_ref      	REAL,
                        _refine_ls_restrained_S_all        		REAL,
                        _refine_ls_shift_su_max            		REAL,
                        _refine_ls_shift_su_mean           		REAL,
                        _refine_diff_density_max                REAL,
                        _refine_diff_density_min                REAL,
                        _diffrn_reflns_av_unetI_netI            REAL,
                        _database_code_depnum_ccdc_archive      TEXT,
                        _shelx_res_file                         TEXT,
                        modification_time                       DATE,
                        file_size                               INTEGER,
                    PRIMARY KEY(Id),
                      FOREIGN KEY(StructureId)
                        REFERENCES Structure(Id)
                          ON DELETE CASCADE
                          ON UPDATE NO ACTION);
                    ''')

        self.cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS cell (
                Id              INTEGER NOT NULL,
                StructureId     INTEGER NOT NULL,
                a               REAL,
                b               REAL,
                c               REAL,
                alpha           REAL,
                beta            REAL,
                gamma           REAL,
                volume          REAL,
            PRIMARY KEY(Id),
              FOREIGN KEY(StructureId)
                REFERENCES Structure(Id)
                  ON DELETE CASCADE
                  ON UPDATE NO ACTION);
            '''
        )

        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS authors (
                Id                          INTEGER NOT NULL,
                StructureId                 INTEGER NOT NULL,
                _audit_author_name          TEXT,
                _audit_contact_author_name  TEXT,
                _publ_contact_author_name   TEXT,
                _publ_contact_author        TEXT,
                _publ_author_name           TEXT,
            PRIMARY KEY(Id),
                FOREIGN KEY(StructureId)
                REFERENCES Structure(Id)
                    ON DELETE CASCADE 
                    ON UPDATE NO ACTION);
            """
        )

        """self.cur.execute(
                '''
                CREATE TABLE IF NOT EXISTS niggli_cell (
                            Id        INTEGER NOT NULL,
                            StructureId    INTEGER NOT NULL,
                            a    FLOAT,
                            b    FLOAT,
                            c    FLOAT,
                            alpha   FLOAT,
                            beta    FLOAT,
                            gamma   FLOAT,
                            volume     FLOAT,
                        PRIMARY KEY(Id),
                          FOREIGN KEY(StructureId)
                            REFERENCES niggli_cell(Id)
                              ON DELETE CASCADE
                              ON UPDATE NO ACTION);
                '''
        )"""

        self.cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS sum_formula (
                    Id             INTEGER NOT NULL,
                    StructureId    INTEGER NOT NULL,
                    {}             REAL,
                    PRIMARY KEY(Id),
                      FOREIGN KEY (StructureId)
                        REFERENCES Structure(Id)
                          ON DELETE CASCADE
                          ON UPDATE NO ACTION);
            '''.format("   FLOAT, ".join(["'Elem_" + at + "'" for at in sorted_atoms]))
        )

    def init_textsearch(self):
        """
        Initializes the full text search (fts) tables.
        """
        self.cur.execute("DROP TABLE IF EXISTS txtsearch")

        # The simple tokenizer is best for my purposes (A self-written tokenizer would even be better):
        self.cur.execute("""
            CREATE VIRTUAL TABLE txtsearch USING
                    fts4(StructureId    INTEGER,
                         filename       TEXT,
                         dataname       TEXT,
                         path           TEXT,
                         shelx_res_file TEXT,
                            tokenize=simple "tokenchars= .=-_");
                          """)

    def init_author_search(self):
        """
        Initializes the full text search (fts) table for author search.
        """
        self.cur.execute("DROP TABLE IF EXISTS authortxtsearch")

        # The simple tokenizer is best for my purposes (A self-written tokenizer would even be better):
        self.cur.execute("""
            CREATE VIRTUAL TABLE authortxtsearch USING
                    fts4(StructureId                   INTEGER,
                         _audit_author_name            TEXT,
                         _audit_contact_author_name    TEXT,
                         _publ_contact_author_name     TEXT,
                         _publ_contact_author          TEXT,
                         _publ_author_name             TEXT,
                            tokenize=simple "tokenchars= .=-_");
                          """)

    def make_indexes(self):
        """ Databse indexes for faster searching
        """
        self.cur.execute("""DROP INDEX if exists idx_a""")
        self.cur.execute("""DROP INDEX if exists idx_b""")
        self.cur.execute("""DROP INDEX if exists idx_c""")
        self.cur.execute("""DROP INDEX if exists idx_al""")
        self.cur.execute("""DROP INDEX if exists idx_be""")
        self.cur.execute("""DROP INDEX if exists idx_ga""")
        self.cur.execute("""DROP INDEX if exists idx_volume""")
        self.cur.execute("""DROP INDEX if exists idx_sumform""")
        self.cur.execute("""DROP INDEX if exists idx_spgr""")
        self.cur.execute("""DROP INDEX if exists idx_modiftime""")
        self.cur.execute("""DROP INDEX if exists idx_itnum""")
        self.cur.execute("""DROP INDEX if exists idx_ccd""")
        self.cur.execute("""CREATE INDEX idx_volume ON cell (volume)""")
        self.cur.execute("""CREATE INDEX idx_a ON cell (a)""")
        self.cur.execute("""CREATE INDEX idx_b ON cell (b)""")
        self.cur.execute("""CREATE INDEX idx_c ON cell (c)""")
        self.cur.execute("""CREATE INDEX idx_al ON cell (alpha)""")
        self.cur.execute("""CREATE INDEX idx_be ON cell (beta)""")
        self.cur.execute("""CREATE INDEX idx_ga ON cell (gamma)""")
        self.cur.execute("""CREATE INDEX idx_spgr ON Residuals (_space_group_IT_number)""")
        self.cur.execute("""CREATE INDEX idx_modiftime ON Residuals (modification_time)""")
        self.cur.execute("""CREATE INDEX idx_itnum ON Residuals (_space_group_IT_number)""")
        self.cur.execute("""CREATE INDEX idx_ccd ON Residuals (_database_code_depnum_ccdc_archive)""")
        self.con.commit()

    def populate_author_fulltext_search(self):
        index = """
            INSERT INTO authortxtsearch (StructureId,
                                    _audit_author_name,
                                    _audit_contact_author_name,
                                    _publ_contact_author_name,
                                    _publ_contact_author,
                                    _publ_author_name)
            SELECT  aut.StructureId,
                    aut._audit_author_name,
                    aut._audit_contact_author_name,
                    aut._publ_contact_author_name,
                    aut._publ_contact_author,
                    aut._publ_author_name
                        FROM authors AS aut; """
        self.db_request(index)
        self.db_request("""INSERT INTO authortxtsearch(authortxtsearch) VALUES('optimize'); """)

    def populate_fulltext_search_table(self):
        """
        Populates the fts4 table with data to search for text.
        _publ_contact_author_name
        """
        populate_index = """
                    INSERT INTO txtsearch (StructureId,
                                            filename,
                                            dataname,
                                            path,
                                            shelx_res_file)
            SELECT  str.Id,
                    str.filename,
                    str.dataname,
                    str.path,
                    res._shelx_res_file
                        FROM Structure AS str
                            INNER JOIN Residuals AS res WHERE str.Id = res.Id; """
        optimize_queries = """INSERT INTO txtsearch(txtsearch) VALUES('optimize'); """
        self.cur.execute(populate_index)
        self.cur.execute(optimize_queries)

    def get_lastrowid(self) -> int:
        """
        Retrurns the last rowid of a loaded database.
        """
        try:
            return self.db_fetchone("""SELECT max(id) FROM Structure""")[0]
        except (TypeError, IndexError):
            # No database or empty table:
            return 0

    def db_fetchone(self, request, *args):
        """
        fetches one db entry
        """
        try:
            self.cur.execute(request, *args)
        except (OperationalError, ProgrammingError):
            return False
        row = self.cur.fetchone()
        return row

    def db_request(self, request, *args) -> Union[list, tuple, dict]:
        """
        Performs a SQLite3 database request with "request" and optional arguments
        to insert parameters via "?" into the database request.
        A push request will return the last row-Id.
        A pull request will return the requested rows
        :param request: sqlite database request like:
                    '''SELECT Structure.cell FROM Structure'''
        :type request: str
        """
        try:
            if DEBUG:
                print('db request:', request, 'args:', args)
            self.cur.execute(request, *args)
            # last_rowid = self.cur.lastrowid
        except OperationalError as e:
            print(e, "\nDB execution error")
            print('Request:', request)
            print('Arguments:', args)
            return []
        rows = self.cur.fetchall()
        if not rows:
            return tuple()
            # return last_rowid
        else:
            return rows

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            key = col[0]
            if isinstance(row[idx], bytes):
                d[key] = row[idx].decode('utf-8', 'ignore')
            else:
                d[key] = row[idx]
        return d

    def __del__(self):
        # commit is very slow:
        try:
            self.con.commit()
        except (AttributeError, ProgrammingError):
            pass
        try:
            self.con.close()
        except (AttributeError, ProgrammingError):
            pass

    def commit_db(self, comment=""):
        self.con.commit()
        if comment:
            print(comment)


##################################################################


class StructureTable():
    """
    handles structure in and output from the database
    """

    def __init__(self, dbfile):
        """
        Class to modify the database tables of the cell database in "dbfile"
        :param dbfile: database file path
        :type dbfile: str
        """
        self.dbfilename = dbfile
        self.database = DatabaseRequest(dbfile)

    def __len__(self):
        """
        Number of structures in the database.
        """
        try:
            return self.database.db_fetchone('SELECT COUNT(*) FROM Structure')[0]
        except TypeError:
            return 0

    def __getitem__(self, str_id):
        try:
            str_id = int(str_id)
        except(ValueError, KeyError):
            print('Wrong type. Integer expected')
            sys.exit()
        if str_id < 0:
            str_id = len(self) - abs(str_id)
        found = self.get_filepath(str_id)
        if found:
            return found

    def get_all_structures_as_dict(self, ids: (list, tuple) = None) -> dict:
        """
        Returns the list of structures as dictionary.

        >>> str = StructureTable('tests/test-data/test.sql')
        >>> len(str.get_all_structures_as_dict([1,2]))
        2
        """
        self.database.con.row_factory = self.database.dict_factory
        self.database.cur = self.database.con.cursor()
        req = '''SELECT str.Id AS recid, str.path, str.filename, str.dataname, res.modification_time
                        FROM Structure AS str 
                        INNER JOIN Residuals as res ON res.StructureId == recid '''
        if ids:
            ids = tuple(ids)
            placeholders = ', '.join('?' * len(ids))
            req = req + f''' WHERE str.Id in ({placeholders})'''
            rows = self.database.db_request(req, ids)
        else:
            rows = self.database.db_request(req)
        self.database.cur.close()
        # setting row_factory back to regular touple base requests:
        self.database.con.row_factory = None
        self.database.cur = self.database.con.cursor()
        return rows

    def get_structures_by_idlist(self, ids: Union[List, Tuple]):
        return self.get_all_structure_names(ids) if ids else []

    def get_all_structure_names(self, ids: list = None) -> List:
        """
        returns all fragment names in the database, sorted by name
        :returns [id, meas, path, filename, data]
        >>> str = StructureTable('tests/test-data/test.sql')
        >>> len(str.get_all_structure_names([1, 2]))
        2
        """
        req = '''SELECT str.Id, str.dataname, str.filename, res.modification_time, str.path
                        FROM Structure AS str 
                        INNER JOIN Residuals AS res ON res.StructureId == str.Id '''
        if ids:
            ids = tuple(ids)
            placeholders = ', '.join('?' * len(ids))
            req = req + f''' WHERE str.Id in ({placeholders})'''
            rows = self.database.db_request(req, ids)
            return rows
        return self.database.db_request(req)

    def get_filepath(self, structure_id) -> str:
        """
        returns the path of a res file in the db
        """
        req_path = '''SELECT dataname, path FROM Structure WHERE Structure.Id = {0}'''.format(structure_id)
        path = self.database.db_request(req_path)[0]
        return path

    def fill_structures_table(self, path: str, filename: str, structure_id: int, measurement_id: int, dataname: str):
        """
        Fills a structure into the database.
        """
        req = '''
              INSERT INTO Structure (Id, measurement, filename, path, dataname) VALUES(?, ?, ?, ?, ?)
              '''
        filename = filename.encode(db_enoding, "ignore")  # .encode("utf-8", "surrogateescape")
        path = path.encode(db_enoding, "ignore")
        dataname = dataname.encode(db_enoding, "ignore")
        self.database.db_request(req, (structure_id, measurement_id, filename, path, dataname))
        return structure_id

    def fill_measuremnts_table(self, name: str, structure_id):
        """
        Fills a measurements into the database.
        """
        req = '''
              INSERT INTO measurement (Id, name) VALUES(?, ?)
              '''
        name = name.encode(db_enoding, "surrogateescape")
        self.database.db_request(req, (structure_id, name))
        return structure_id

    def fill_cell_table(self, structure_id: int, a: float, b: float, c: float, alpha: float, beta: float, gamma: float,
                        volume: float):
        """
        fill the cell of structure(structureId) in the table
        cell = [a, b, c, alpha, beta, gamma]
        """
        req = '''INSERT INTO cell (StructureId, a, b, c, alpha, beta, gamma, volume) 
                            VALUES(?, ?, ?, ?, ?, ?, ?, ?)'''
        if self.database.db_request(req, (structure_id, a, b, c, alpha, beta, gamma, volume)):
            return True

    def fill_niggli_cell_table(self, structure_id: int, a: float, b: float, c: float, alpha: float, beta: float,
                               gamma: float, volume: float):
        """
        Fill the cell of structure(structureId) in the table with the reduced niggli cell.

        :returns True if successful
        """
        req = '''INSERT INTO niggli_cell (StructureId, a, b, c, alpha, beta, gamma, volume) 
                                    VALUES(?, ?, ?, ?, ?, ?, ?, ?)'''
        if self.database.db_request(req, (structure_id, a, b, c, alpha, beta, gamma, volume)):
            return True

    def fill_atoms_table(self, structure_id: int, name: str, element: str, x: float, y: float, z: float, occ: float,
                         part: int, xc: float, yc: float, zc: float):
        """
        Fill the atoms into the Atoms table.
        """
        req = '''INSERT INTO Atoms (StructureId, name, element, x, y, z, occupancy, part, xc, yc, zc) 
                                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        if self.database.db_request(req, (structure_id, name, element, x, y, z, occ, part, xc, yc, zc)):
            return True

    def get_atoms_table(self, structure_id, cartesian=False, as_list=False) -> Union[List, Tuple]:
        """
        returns the atoms of structure with structure_id
        returns: [Name, Element, X, Y, Z, Part, ocuupancy]
        """
        fractional = 'x, y, z'
        cart_coords = 'xc, yc, zc'
        req = """SELECT Name, element, {}, CAST(part as integer), occupancy 
                              FROM Atoms WHERE StructureId = ?"""
        if cartesian:
            result = self.database.db_request(req.format(cart_coords), (structure_id,))
        else:
            result = self.database.db_request(req.format(fractional), (structure_id,))
        if as_list:
            return [list(x) for x in result]
        else:
            return result

    def fill_formula(self, structure_id, formula: dict):
        """
        Fills data into the sum formula table.
        """
        out = []
        for x in formula:
            if x.capitalize() not in sorted_atoms:
                out.append(x)
        # Delete non-existing atoms from formula:
        for x in out:
            del formula[x]
        if not formula:
            return []
        columns = ', '.join(['Elem_' + x.capitalize() for x in formula.keys()])
        placeholders = ', '.join('?' * (len(formula) + 1))
        req = f'''INSERT INTO sum_formula (StructureId, {columns}) VALUES ({placeholders});'''
        result = self.database.db_request(req, [structure_id] + list(formula.values()))
        return result

    def get_calc_sum_formula(self, structure_id: int) -> dict:
        """
        Returns the sum formula of an entry as dictionary.
        """
        request = """SELECT * FROM sum_formula WHERE StructureId = ?"""
        dic = self.get_dict_from_request(request, structure_id)
        return dic

    def get_cif_sumform_by_id(self, structure_id):
        """
        returns the cell of a res file in the db

        >>> db = StructureTable('./tests/test-data/test.sql')
        >>> db.get_cif_sumform_by_id(16)
        ('C18 H19 N O4',)
        """
        if not structure_id:
            return False
        req = '''SELECT _chemical_formula_sum FROM Residuals WHERE StructureId = ?'''
        cell = self.database.db_request(req, (structure_id,))
        if cell and len(cell) > 0:
            return cell[0]
        else:
            return cell

    def fill_residuals_table(self, structure_id, cif):
        """
        Fill the table with residuals of the refinement.
        """
        if cif.cif_data['calculated_formula_sum']:
            self.fill_formula(structure_id, cif.cif_data['calculated_formula_sum'])
        residuals = """
                    (
                    StructureId,
                    _cell_formula_units_Z,
                    _space_group_name_H_M_alt,
                    _space_group_name_Hall,
                    _space_group_centring_type,
                    _space_group_IT_number,
                    _space_group_crystal_system,
                    _space_group_symop_operation_xyz,
                    _chemical_formula_sum,
                    _chemical_formula_weight,
                    _exptl_crystal_description,
                    _exptl_crystal_colour,
                    _exptl_crystal_size_max,
                    _exptl_crystal_size_mid,
                    _exptl_crystal_size_min,
                    _audit_creation_method,
                    _exptl_absorpt_coefficient_mu,
                    _exptl_absorpt_correction_type,
                    _diffrn_ambient_temperature,
                    _diffrn_radiation_wavelength,
                    _diffrn_radiation_type,
                    _diffrn_source,
                    _diffrn_measurement_device_type,
                    _diffrn_reflns_number,
                    _diffrn_reflns_av_R_equivalents,
                    _diffrn_reflns_theta_min,
                    _diffrn_reflns_theta_max,
                    _diffrn_reflns_theta_full,
                    _diffrn_measured_fraction_theta_max,
                    _diffrn_measured_fraction_theta_full,
                    _reflns_number_total,
                    _reflns_number_gt,
                    _reflns_threshold_expression,
                    _reflns_Friedel_coverage,
                    _computing_structure_solution,
                    _computing_structure_refinement,
                    _refine_special_details,
                    _refine_ls_abs_structure_Flack,
                    _refine_ls_structure_factor_coef,
                    _refine_ls_weighting_details,
                    _refine_ls_number_reflns,
                    _refine_ls_number_parameters,
                    _refine_ls_number_restraints,
                    _refine_ls_R_factor_all,
                    _refine_ls_R_factor_gt,
                    _refine_ls_wR_factor_ref,
                    _refine_ls_wR_factor_gt,
                    _refine_ls_goodness_of_fit_ref,
                    _refine_ls_restrained_S_all,
                    _refine_ls_shift_su_max,
                    _refine_ls_shift_su_mean,
                    _refine_diff_density_max,
                    _refine_diff_density_min,
                    _diffrn_reflns_av_unetI_netI,
                    _database_code_depnum_ccdc_archive,
                    _shelx_res_file,
                    modification_time,
                    file_size
                    ) 
                    """
        req = '''INSERT INTO Residuals {} VALUES ({});'''.format(residuals, self.joined_arglist(residuals.split(',')))

        result = self.database.db_request(req, (
            structure_id,
            cif.cif_data['_cell_formula_units_Z'],  # Z
            cif.cif_data['_space_group_name_H-M_alt'],  # Raumgruppe (Herman-Maugin)
            cif.cif_data['_space_group_name_Hall'],  # Hall-Symbol
            cif.cif_data['_space_group_centring_type'],  # Lattice centering
            cif.cif_data['_space_group_IT_number'],  # Raumgruppen-Nummer aus IT
            cif.cif_data['_space_group_crystal_system'],  # Kristallsystem
            cif.cif_data['_space_group_symop_operation_xyz'],  # SYMM cards
            cif.cif_data['_chemical_formula_sum'],  # Summenformel
            cif.cif_data['_chemical_formula_weight'],  # Moyety-Formel
            cif.cif_data['_exptl_crystal_description'],  # Habitus
            cif.cif_data['_exptl_crystal_colour'],  # Farbe
            cif.cif_data['_exptl_crystal_size_max'],  # Größe
            cif.cif_data['_exptl_crystal_size_mid'],  # Größe
            cif.cif_data['_exptl_crystal_size_min'],  # Größe
            cif.cif_data['_audit_creation_method'],  # how data were entered into the data block.
            cif.cif_data['_exptl_absorpt_coefficient_mu'],  # Linear absorption coefficient (mm-1)
            cif.cif_data['_exptl_absorpt_correction_type'],  # Code for absorption correction
            cif.cif_data['_diffrn_ambient_temperature'],  # The mean temperature in kelvins at which the
            # intensities were measured.
            cif.cif_data['_diffrn_radiation_wavelength'],  # Radiation wavelength (Å)
            cif.cif_data['_diffrn_radiation_type'],  # Radiation type (e.g. neutron or `Mo Kα')
            cif.cif_data['_diffrn_source'],  # Röntgenquelle
            cif.cif_data['_diffrn_measurement_device_type'],  # Diffractometer make and type
            cif.cif_data['_diffrn_reflns_number'],  # Total number of reflections measured excluding systematic absences
            cif.cif_data['_diffrn_reflns_av_R_equivalents'],  # R(int) -> R factor for symmetry-equivalent intensities
            cif.cif_data['_diffrn_reflns_theta_min'],  # Minimum θ of measured reflections (°)
            cif.cif_data['_diffrn_reflns_theta_max'],  # Maximum θ of measured reflections (°)
            cif.cif_data['_diffrn_reflns_theta_full'],
            # θ to which available reflections are close to 100% complete (°)
            cif.cif_data['_diffrn_measured_fraction_theta_max'],
            # completeness, Fraction of unique reflections measured to θmax
            cif.cif_data['_diffrn_measured_fraction_theta_full'],  # Fraction of unique reflections measured to θfull
            cif.cif_data['_reflns_number_total'],  # Number of symmetry-independent reflections excluding
            #   systematic absences.
            cif.cif_data['_reflns_number_gt'],  # Number of reflections > σ threshold
            cif.cif_data['_reflns_threshold_expression'],  # σ expression for F, F2 or I threshold
            cif.cif_data['_reflns_Friedel_coverage'],  # The proportion of Friedel-related reflections
            #   present in the number of reported unique reflections
            cif.cif_data['_computing_structure_solution'],  # Reference to structure-solution software
            cif.cif_data['_computing_structure_refinement'],  # Reference to structure-refinement software
            cif.cif_data['_refine_special_details'],  # Details about the refinement
            cif.cif_data['_refine_ls_abs_structure_Flack'],
            cif.cif_data['_refine_ls_structure_factor_coef'],  # Code for F, F2 or I used in least-squares refinement
            cif.cif_data['_refine_ls_weighting_details'],  # Weighting expression
            cif.cif_data['_refine_ls_number_reflns'],  # The number of unique reflections contributing to the
            #   least-squares refinement calculation.
            cif.cif_data['_refine_ls_number_parameters'],  # Number of parameters refined
            cif.cif_data['_refine_ls_number_restraints'],  # Number of restraints applied during refinement
            cif.cif_data['_refine_ls_R_factor_all'],
            cif.cif_data['_refine_ls_R_factor_gt'],  # R1 factor of F for reflections > threshold
            cif.cif_data['_refine_ls_wR_factor_ref'],  # wR2 factor of coefficient for refinement reflections
            cif.cif_data['_refine_ls_wR_factor_gt'],
            cif.cif_data['_refine_ls_goodness_of_fit_ref'],  # Goodness of fit S for refinement reflections
            cif.cif_data['_refine_ls_restrained_S_all'],  # The least-squares goodness-of-fit parameter S' for
            # all reflections after the final cycle of least-squares refinement.
            cif.cif_data['_refine_ls_shift/su_max'],  # Maximum shift/s.u. ratio after final refinement cycle
            cif.cif_data['_refine_ls_shift/su_mean'],
            cif.cif_data['_refine_diff_density_max'],  # Maximum difference density after refinement
            cif.cif_data['_refine_diff_density_min'],  # Deepest hole
            cif.cif_data['_diffrn_reflns_av_unetI/netI'],  # R(sigma)
            cif.cif_data['_database_code_depnum_ccdc_archive'],  # CCDC number
            cif.cif_data['_shelx_res_file'],  # The content of the SHELXL res file
            cif.cif_data['modification_time'],
            cif.cif_data['file_size']
        )
                                          )
        return result

    def fill_authors_table(self, structure_id: int, cif: CifFile):
        """
        This is the table where the direct values from the authors of the CIF are stored.
        The virtual table "authortxtsearch" conteins the fts data.
        """
        req = '''INSERT INTO authors (StructureId,
                                      _audit_author_name, 
                                      _audit_contact_author_name, 
                                      _publ_contact_author_name,
                                      _publ_contact_author, 
                                      _publ_author_name) 
                            VALUES(?, ?, ?, ?, ?, ?)
        '''
        self.database.db_request(req, (structure_id,
                                       cif.cif_data.get('_audit_author_name'),
                                       cif.cif_data.get('_audit_contact_author_name'),
                                       cif.cif_data.get('_publ_contact_author_name'),
                                       cif.cif_data.get('_publ_contact_author'),
                                       cif.cif_data.get('_publ_author_name')))

    def get_row_as_dict(self, structure_id):
        """
        Returns a database row from residuals table as dictionary.
        """
        request = """select * from residuals where StructureId = ?"""
        # setting row_factory to dict for the cif keys:
        dic = self.get_dict_from_request(request, structure_id)
        authors = self.get_dict_from_request('''SELECT * FROM authors WHERE StructureId = ?''', structure_id)
        if authors and dic:
            dic.update(authors)
        return dic

    def get_dict_from_request(self, request: str, structure_id: int) -> Dict:
        """
        Retruns the result of the given database request as dictionary.
        """
        # setting row_factory to dict_factory
        self.database.con.row_factory = self.database.dict_factory
        self.database.cur = self.database.con.cursor()
        dic = {}
        try:
            dic = self.database.db_fetchone(request, (structure_id,))
        except (ValueError, InterfaceError) as e:
            print(e, '###')
        self.database.cur.close()
        # setting row_factory back to regular touple base requests:
        self.database.con.row_factory = None
        self.database.cur = self.database.con.cursor()
        return dic

    def get_cell_as_dict(self, structure_id):
        """
        Returns a database row as dictionary
        """
        request = """select * from cell where StructureId = ?"""
        # setting row_factory to dict for the cif keys:
        dic = self.get_dict_from_request(request, structure_id)
        return dic

    @staticmethod
    def joined_arglist(items):
        """
        Retruns a string of ?, with the length of the input list.
        """
        return ', '.join(['?'] * len(items))

    def get_cells_as_list(self, structure_ids: list):
        """
        Returns a list of unit cells from the list of input ids.
        """
        req = 'select a, b, c, alpha, beta, gamma, volume from cell where StructureId IN ({seq})'.format(
            seq=self.joined_arglist(structure_ids))
        return self.database.db_request(req, structure_ids)

    def get_cell_by_id(self, structure_id):
        """
        returns the cell of a res file in the db
        """
        if not structure_id:
            return False
        req = '''SELECT a, b, c, alpha, beta, gamma, volume FROM cell WHERE StructureId = ?'''
        cell = self.database.db_request(req, (structure_id,))
        if cell and len(cell) > 0:
            return cell[0]
        else:
            return cell

    def find_by_volume(self, volume: float, threshold: float = 0) -> List:
        """
        Searches cells with volume between upper and lower limit. Returns the Id and the unit cell.
        :param threshold: Volume uncertaincy where to search
        :param volume: the unit cell volume
        """
        if not threshold:
            threshold = log(volume) + 1.0
        upper_limit = float(volume + threshold)
        lower_limit = float(volume - threshold)
        req = '''SELECT StructureId, a, b, c, alpha, beta, gamma, volume FROM cell WHERE cell.volume >= ? AND cell.volume <= ?'''
        try:
            return self.database.db_request(req, (lower_limit, upper_limit))
        except(TypeError, KeyError):
            # print("Wrong volume for cell search.")
            return []

    def find_by_niggli_cell(self, a, b, c, alpha, beta, gamma, axtol=0.02, angtol=0.025, maxsolutions=None):
        """
        Searches cells with certain deviations in the unit cell parameters.
        #>>> db = StructureTable('./tests/test-data/test.sql')
        #>>> vol = [7.878, 10.469, 16.068, 90.000, 95.147, 90.000]
        #>>> db.find_by_niggli_cell(*vol)
        [8, 201, 202]
        """
        mina, minb, minc = [x - (x * axtol) for x in [a, b, c]]
        maxa, maxb, maxc = [x + (x * axtol) for x in [a, b, c]]
        minal, minbe, minga = [x - (x * angtol) for x in [alpha, beta, gamma]]
        maxal, maxbe, maxga = [x + (x * angtol) for x in [alpha, beta, gamma]]
        req = '''SELECT cell.StructureId, cell.a, cell.b, cell.c, cell.alpha, cell.beta, cell.gamma, 
                        res._space_group_IT_number, cell.volume, stru.filename
                                    FROM cell as cell
                                        INNER JOIN niggli_cell as ni ON cell.Id = ni.StructureId
                                                       and (ni.a BETWEEN ? and ?)
                                                       and (ni.b BETWEEN  ? and ?)
                                                       and (ni.c BETWEEN  ? and ?)
                                                       and (ni.alpha BETWEEN  ? and ?)
                                                       and (ni.beta BETWEEN  ? and ?)
                                                       and (ni.gamma BETWEEN  ? and ?)
                                        INNER JOIN Structure as stru ON cell.StructureId = stru.Id
                                        INNER JOIN Residuals AS res WHERE cell.StructureId = res.StructureId

              '''
        try:
            result = self.database.db_request(req, (
                mina, maxa, minb, maxb, minc, maxc, minal, maxal, minbe, maxbe, minga, maxga))
            if maxsolutions:
                return result[:maxsolutions]
            else:
                return result
        except(TypeError, KeyError):
            return ()

    def find_by_ccdc_num(self, ccdc: str) -> list:
        """
        Find structures with respective CCDC number.
        """
        req = """
        SELECT StructureId FROM Residuals WHERE _database_code_depnum_ccdc_archive LIKE ?
        """
        result = self.database.db_request(req, ('%' + ccdc + '%',))
        return self.result_to_list(result)

    def find_by_strings(self, text: str) -> Tuple:
        """
        Searches cells with volume between upper and lower limit
        :param text: Volume uncertaincy where to search
        id, name, data, path
        """
        req = '''
        SELECT StructureId FROM txtsearch 
            WHERE filename MATCH ? 
                OR dataname MATCH ? 
                OR path MATCH ?
                OR shelx_res_file MATCH ?
        '''
        try:
            res = self.database.db_request(req, (text, text, text, text))
        except (TypeError, ProgrammingError, OperationalError) as e:
            print('DB request error in find_by_strings().', e)
            return tuple()
        return tuple(self.result_to_list(res))

    def find_authors(self, text: str) -> Tuple:
        author_table_exists = self.database.db_request("""SELECT name FROM sqlite_master WHERE 
                        type='table' AND name='authortxtsearch';""")
        if not author_table_exists:
            return tuple()
        search = f"{'*'}{text}{'*'}"
        select = """SELECT StructureId from authortxtsearch """
        req = f'''
            {select}
                WHERE _audit_author_name MATCH ? 
                UNION
            {select}
                WHERE _audit_contact_author_name MATCH ?
                UNION
            {select}
                WHERE _publ_contact_author_name MATCH ?
                UNION
            {select}
                WHERE _publ_contact_author MATCH ?
                UNION
            {select}
                WHERE _publ_author_name MATCH ?
        '''
        try:
            res = self.database.db_request(req, (search, search, search, search, search))
        except (TypeError, ProgrammingError, OperationalError) as e:
            print('DB request error in find_by_strings().', e)
            return ()
        return tuple(self.result_to_list(res))

    def find_text_and_authors(self, txt: str) -> tuple:
        result_txt = self.find_authors(txt)
        result_authors = self.find_by_strings(txt)
        result_txt = set(result_txt)
        result_txt.update(result_authors)
        return tuple(result_txt)

    def find_by_it_number(self, number: int) -> List[int]:
        """
        Find structures by space group number in international tables of
        crystallography.
        Returns a list of index numbers.
        """
        try:
            value = int(number)
        except ValueError:
            return []
        req = '''SELECT StructureId from Residuals WHERE _space_group_IT_number IS ?'''
        result = self.database.db_request(req, (value,))
        return self.result_to_list(result)

    def result_to_list(self, result: Union[List, Tuple]) -> List:
        if result and len(result) > 0:
            return [x[0] for x in result]
        else:
            return []

    def find_by_elements(self, elements: list, excluding: list = None, onlyincluded: bool = False) -> List[int]:
        """
        Find structures where certain elements are included in the sum formula.
        """
        if not excluding:
            excluding = []
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
        result = self.database.db_request(req)
        return self.result_to_list(result)

    def find_by_date(self, start='0000-01-01', end='NOW') -> List:
        """
        Find structures between start and end date.
        """
        req = """
              SELECT StructureId FROM Residuals WHERE modification_time between DATE(?) AND DATE(?);
              """
        result = self.database.db_request(req, (start, end))
        return self.result_to_list(result)

    def find_by_rvalue(self, rvalue: float) -> List:
        """
        Finds structures with R1 value better than rvalue. I search both R1 values, because often one or even both
        are missing.
        """
        req = """
                SELECT StructureId FROM Residuals WHERE _refine_ls_R_factor_gt <= ? OR _refine_ls_R_factor_all <= ?
                """
        return self.result_to_list(self.database.db_request(req, (rvalue, rvalue)))

    def find_biggest_cell(self):
        """
        Finds the structure with the biggest cell in the db. This should be done by volume, but was
        just for fun...
        """
        req = '''SELECT Id, a, b, c FROM cell GROUP BY Id ORDER BY a, b, c ASC'''
        result = self.database.db_request(req)
        if result:
            return result[-1]
        else:
            return False

    def get_largest_id(self):
        req = """SELECT max(Id) FROM Structure"""
        result = self.database.db_request(req)
        if result:
            return result[-1][-1]
        else:
            return 0

    def get_database_version(self) -> int:
        """
        Returns a version nu,ber for database revisions.
        """
        req = """
              SELECT Format FROM database_format;
              """
        try:
            version: int = self.database.db_request(req)[0][0]
        except IndexError:
            version: int = 0
        return version

    def set_database_version(self, version=0):
        """
        Database version to indicate apex or other formats. A value of 1 means the data is from APEX.
        """
        req = """
              INSERT or REPLACE into database_format (Id, Format) values (?, ?)
              """
        self.database.db_request(req, (1, version))

    def get_cif_export_data(self, structure_id):
        try:
            data_name = bytes(self.get_all_structure_names([structure_id])[0][4]).decode('ascii', 'ignore')
        except IndexError:
            data_name = ''
        data_name = data_name.replace(' ', '_')
        cif = self.get_row_as_dict(structure_id)
        cell = self.get_cell_by_id(structure_id)
        cif['data'] = data_name
        cif['_cell_length_a'] = cell[0]
        cif['_cell_length_b'] = cell[1]
        cif['_cell_length_c'] = cell[2]
        cif['_cell_angle_alpha'] = cell[3]
        cif['_cell_angle_beta'] = cell[4]
        cif['_cell_angle_gamma'] = cell[5]
        cif['_cell_volume'] = cell[6]
        # Sort the dictionary to have the pairs sorted in the CIF:
        cif = dict(sorted(cif.items(), key=lambda kv: kv[0]))
        atoms = self.get_atoms_table(structure_id, cartesian=False, as_list=False)
        cif['_loop'] = []
        # Atoms can be empty:
        if atoms:
            for atom in atoms:
                try:
                    cif['_loop'].append({'_atom_site_label'         : str(atom[0]),
                                         '_atom_site_type_symbol'   : str(atom[1]),
                                         '_atom_site_fract_x'       : str(atom[2]),
                                         '_atom_site_fract_y'       : str(atom[3]),
                                         '_atom_site_fract_z'       : str(atom[4]),
                                         '_atom_site_disorder_group': str(atom[5]),
                                         '_atom_site_occupancy'     : str(atom[6]),
                                         })
                except(IndexError, ValueError):
                    pass
        return cif


if __name__ == '__main__':
    # searcher.filecrawler.put_cifs_in_db(searchpath='../')
    db = StructureTable('./test.sqlite')
    f = db.database.db_request("""SELECT name FROM sqlite_master WHERE type='table' AND name='authortxtsearch';""")
    print(f)
    # db.initialize_db()
    # db = StructureTable(r'C:\Program Files (x86)\CCDC\CellCheckCSD\cell_check.csdsql')
    # db.initialize_db()
    # db = StructureTable('../structurefinder.sqlite')
    # db.database.initialize_db()
    # out = db.find_by_date(start="2017-08-19")
    # out = db.get_cell_by_id(12)
    # out = db.find_by_strings('dk')
    ############################################
    # elinclude = ['C', 'O', 'N', 'F']
    # elexclude = ['Tm']
    # inc = db.find_by_elements(elinclude, excluding=False)
    # exc = db.find_by_elements(elinclude, ['Al'])
    # print('include: {}'.format(sorted(inc)))
    # print('exclude: {}'.format(sorted(exc)))
    # combi = set(inc) - set(exc)
    # print(combi)
    # print(len(combi))
    #########################################
    # db.fill_formula(1, {'StructureId': 1, 'C': 34.0, 'H': 24.0, 'O': 4.0, 'F': 35.99999999999999, 'AL': 1.0, 'GA': 1.0})
    # form = db.get_sum_formula(5)
    # print(exc)
    # req = """SELECT Id FROM NORMALISED_REDUCED_CELLS WHERE Volume >= ? AND Volume <= ?"""
    # result = db.database.db_request(req, (1473.46, 1564.76))
    # result = db.find_authors('herb')
    # result = db.find_by_strings('SADI')
    print(db.get_row_as_dict(2))
    # lattice1 = Lattice.from_parameters_niggli_reduced(*cell)
