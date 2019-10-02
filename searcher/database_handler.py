# -*- coding: utf-8 -*-
"""
Created on 09.02.2015

 ----------------------------------------------------------------------------
* "THE BEER-WARE LICENSE" (Revision 42):
* <daniel.kratzert@uni-freiburg.de> wrote this file. As long as you retain this
* notice you can do whatever you want with this stuff. If we meet some day, and
* you think this stuff is worth it, you can buy me a beer in return.
* ----------------------------------------------------------------------------

@author: daniel
"""

import sys
from sqlite3 import OperationalError, ProgrammingError, connect, InterfaceError
from typing import List, Union

from searcher.atoms import sorted_atoms

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
        self.con = connect(dbfile)
        # self.con.execute("PRAGMA foreign_keys = ON")
        # self.con.text_factory = str
        # self.con.text_factory = bytes
        with self.con:
            # set the database cursor
            self.cur = self.con.cursor()

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
                        x          FLOAT,
                        y          FLOAT,
                        z          FLOAT,
                        occupancy  FLOAT,
                        part       INTEGER,
                        xc         FLOAT,
                        yc         FLOAT,
                        zc         FLOAT,
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
                    REFERENCES Structure(Id)
                      ON DELETE CASCADE
                      ON UPDATE NO ACTION);
                '''
        )

        self.cur.execute(
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
        )

        self.cur.execute(
                '''
                CREATE TABLE IF NOT EXISTS sum_formula (
                        Id             INTEGER NOT NULL,
                        StructureId    INTEGER NOT NULL,
                        {}             FLOAT,
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
                          """
                         )

    def get_lastrowid(self):
        """
        Retrurns the last rowid of a loaded database.

        >>> db = DatabaseRequest('./test-data/test.sql')
        >>> db.get_lastrowid()
        263
        """
        lastid = self.db_fetchone("""SELECT max(id) FROM Structure""")
        try:
            return lastid[0]
        except TypeError:
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

    def db_request(self, request, *args) -> (list, tuple):
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
        except ProgrammingError:
            pass
        try:
            self.con.close()
        except ProgrammingError:
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
        Number of database entries.
        """
        return self.database.get_lastrowid()

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

    def get_all_structures_as_dict(self, ids: (list, tuple) = None, all=False) -> list:
        """
        Returns the list of structures as dictionary.

        >>> str = StructureTable('./test-data/test.sql')
        >>> str.get_all_structures_as_dict([16])[0] == {'recid': 16, 'path': '/Users/daniel/GitHub/StructureFinder/test-data/106c.tgz', 'filename': 'ntd106c-P-1-final.cif', 'dataname': 'p-1'}
        True
        """
        self.database.con.row_factory = self.database.dict_factory
        self.database.cur = self.database.con.cursor()
        order = """INNER JOIN Residuals as res ON res.modification_time WHERE recid = res.StructureId
                      ORDER BY res.modification_time DESC"""
        if ids:
            ids = tuple(ids)
            if len(ids) > 1:
                req = '''SELECT Structure.Id AS recid, Structure.path, Structure.filename, 
                             Structure.dataname FROM Structure WHERE Structure.Id in {}'''.format(ids)
            else:
                # only one id
                req = '''SELECT Structure.Id AS recid, Structure.path, Structure.filename, 
                            Structure.dataname FROM Structure WHERE Structure.Id == {}'''.format(ids[0])
        elif all:
            req = '''SELECT Structure.Id AS recid, Structure.path, Structure.filename, 
                      Structure.dataname FROM Structure'''
        else:
            return {}
        rows = self.database.db_request(req)
        self.database.cur.close()
        # setting row_factory back to regular touple base requests:
        self.database.con.row_factory = None
        self.database.cur = self.database.con.cursor()
        return rows

    def get_all_structure_names(self, ids: list = None) -> List[Union[int, int, str, str, str]]:
        """
        returns all fragment names in the database, sorted by name
        :returns [id, meas, path, filename, data]
        """
        order = """INNER JOIN Residuals as res ON res.modification_time WHERE Structure.Id = res.StructureId
                      ORDER BY res.modification_time DESC"""
        if ids:
            if len(ids) > 1:  # a collection of ids
                ids = tuple(ids)
                req = '''SELECT Id, measurement, path, filename, 
                         dataname FROM Structure WHERE Structure.Id in {}'''.format(ids)
            else:  # only one id
                req = '''SELECT Id, measurement, path, filename, dataname FROM Structure WHERE Structure.Id == ?'''
                rows = self.database.db_request(req, ids)
                return rows
        else:  # just all
            req = '''SELECT Id, measurement, path, filename, dataname FROM Structure'''
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

    def get_atoms_table(self, structure_id, cartesian=False, as_list=False):
        """
        returns the atoms of structure with structure_id
        returns: [Name, Element, X, Y, Z, Part, ocuupancy]

        >>> db = StructureTable('./test-data/test.sql')
        >>> db.get_atoms_table(16)[0]
        ('O1', 'O', 0.32157, 0.42645, 0.40201, 0, 1.0)
        """
        req = """SELECT Name, element, x, y, z, CAST(part as integer), occupancy FROM Atoms WHERE StructureId = ?"""
        req_cartesian = """SELECT Name, element, xc, yc, zc, CAST(part as integer), occupancy 
                            FROM Atoms WHERE StructureId = ?"""
        if cartesian:
            result = self.database.db_request(req_cartesian, (structure_id,))
        else:
            result = self.database.db_request(req, (structure_id,))
        if result:
            if as_list:
                return [list(x) for x in result]
            return result
        else:
            return False

    def fill_formula(self, structure_id, formula: dict):
        """
        Fills data into the sum formula table.
        """
        out = []
        for x in formula:
            if not x.capitalize() in sorted_atoms:
                out.append(x)
        # Delete non-existing atoms from formula:
        for x in out:
            del formula[x]
        if not formula:
            return []
        columns = ', '.join(['Elem_' + x.capitalize() for x in formula.keys()])
        placeholders = ', '.join('?' * (len(formula) + 1))
        req = '''INSERT INTO sum_formula (StructureId, {}) VALUES ({});'''.format(columns, placeholders)
        result = self.database.db_request(req, [structure_id] + list(formula.values()))
        return result

    def get_calc_sum_formula(self, structure_id: int) -> dict:
        """
        Returns the sum formula of an entry as dictionary.

        >>> db = StructureTable('./test-data/test.sql')
        >>> sumf = db.get_calc_sum_formula(16)
        >>> sumf == {'Id': 13, 'StructureId': 16, 'Elem_C': 18.0, 'Elem_D': None, 'Elem_H': 19.0, 'Elem_N': 1.0, 'Elem_O': 4.0, 'Elem_Cl': None, 'Elem_Br': None, 'Elem_I': None, 'Elem_F': None, 'Elem_S': None, 'Elem_P': None, 'Elem_Ac': None, 'Elem_Ag': None, 'Elem_Al': None, 'Elem_Am': None, 'Elem_Ar': None, 'Elem_As': None, 'Elem_At': None, 'Elem_Au': None, 'Elem_B': None, 'Elem_Ba': None, 'Elem_Be': None, 'Elem_Bi': None, 'Elem_Bk': None, 'Elem_Ca': None, 'Elem_Cd': None, 'Elem_Ce': None, 'Elem_Cf': None, 'Elem_Cm': None, 'Elem_Co': None, 'Elem_Cr': None, 'Elem_Cs': None, 'Elem_Cu': None, 'Elem_Dy': None, 'Elem_Er': None, 'Elem_Eu': None, 'Elem_Fe': None, 'Elem_Fr': None, 'Elem_Ga': None, 'Elem_Gd': None, 'Elem_Ge': None, 'Elem_He': None, 'Elem_Hf': None, 'Elem_Hg': None, 'Elem_Ho': None, 'Elem_In': None, 'Elem_Ir': None, 'Elem_K': None, 'Elem_Kr': None, 'Elem_La': None, 'Elem_Li': None, 'Elem_Lu': None, 'Elem_Mg': None, 'Elem_Mn': None, 'Elem_Mo': None, 'Elem_Na': None, 'Elem_Nb': None, 'Elem_Nd': None, 'Elem_Ne': None, 'Elem_Ni': None, 'Elem_Np': None, 'Elem_Os': None, 'Elem_Pa': None, 'Elem_Pb': None, 'Elem_Pd': None, 'Elem_Pm': None, 'Elem_Po': None, 'Elem_Pr': None, 'Elem_Pt': None, 'Elem_Pu': None, 'Elem_Ra': None, 'Elem_Rb': None, 'Elem_Re': None, 'Elem_Rh': None, 'Elem_Rn': None, 'Elem_Ru': None, 'Elem_Sb': None, 'Elem_Sc': None, 'Elem_Se': None, 'Elem_Si': None, 'Elem_Sm': None, 'Elem_Sn': None, 'Elem_Sr': None, 'Elem_Ta': None, 'Elem_Tb': None, 'Elem_Tc': None, 'Elem_Te': None, 'Elem_Th': None, 'Elem_Ti': None, 'Elem_Tl': None, 'Elem_Tm': None, 'Elem_U': None, 'Elem_V': None, 'Elem_W': None, 'Elem_Xe': None, 'Elem_Y': None, 'Elem_Yb': None, 'Elem_Zn': None, 'Elem_Zr': None}
        True
        >>> sumf['Id'] == 13
        True
        >>> sumf['Elem_C'] == 18.0
        True
        >>> sumf['Elem_D']

        >>> sumf['Elem_H'] == 19.0
        True
        >>> sumf['Elem_N'] == 1.0
        True
        >>> sumf['Elem_O'] == 4.0
        True
        >>> sumf['Elem_O'] == 5.0
        False
        """
        request = """SELECT * FROM sum_formula WHERE StructureId = ?"""
        dic = self.get_dict_from_request(request, structure_id)
        return dic

    def get_cif_sumform_by_id(self, structure_id):
        """
        returns the cell of a res file in the db

        >>> db = StructureTable('./test-data/test.sql')
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

    def make_indexes(self):
        """ Databse indexes for faster searching
        """
        self.database.cur.execute("""CREATE INDEX idx_volume ON cell (volume)""")
        self.database.cur.execute("""CREATE INDEX idx_a ON cell (a)""")
        self.database.cur.execute("""CREATE INDEX idx_b ON cell (b)""")
        self.database.cur.execute("""CREATE INDEX idx_c ON cell (c)""")
        self.database.cur.execute("""CREATE INDEX idx_al ON cell (alpha)""")
        self.database.cur.execute("""CREATE INDEX idx_be ON cell (beta)""")
        self.database.cur.execute("""CREATE INDEX idx_ga ON cell (gamma)""")
        self.database.cur.execute("""CREATE INDEX idx_volume_n ON niggli_cell (volume)""")
        self.database.cur.execute("""CREATE INDEX idx_a_n ON niggli_cell (a)""")
        self.database.cur.execute("""CREATE INDEX idx_b_n ON niggli_cell (b)""")
        self.database.cur.execute("""CREATE INDEX idx_c_n ON niggli_cell (c)""")
        self.database.cur.execute("""CREATE INDEX idx_al_n ON niggli_cell (alpha)""")
        self.database.cur.execute("""CREATE INDEX idx_be_n ON niggli_cell (beta)""")
        self.database.cur.execute("""CREATE INDEX idx_ga_n ON niggli_cell (gamma)""")
        self.database.cur.execute("""CREATE INDEX idx_sumform ON Residuals (_space_group_IT_number)""")

    def populate_fulltext_search_table(self):
        """
        Populates the fts4 table with data to search for text.
        _publ_contact_author_name
        """
        populate_index = """
                    INSERT INTO txtsearch (
                                StructureId,
                                filename,
                                dataname,
                                path,
                                shelx_res_file
                                )
            SELECT  str.Id,
                    str.filename,
                    str.dataname,
                    str.path,
                    res._shelx_res_file
                        FROM Structure AS str
                            INNER JOIN Residuals AS res WHERE str.Id = res.Id; """
        optimize_queries = """INSERT INTO txtsearch(txtsearch) VALUES('optimize'); """
        self.database.cur.execute(populate_index)
        self.database.cur.execute(optimize_queries)

    def get_row_as_dict(self, structure_id):
        """
        Returns a database row from residuals table as dictionary.
        >>> db = StructureTable('./test-data/test.sql')
        >>> row = db.get_row_as_dict(16)
        """
        request = """select * from residuals where StructureId = ?"""
        # setting row_factory to dict for the cif keys:
        dic = self.get_dict_from_request(request, structure_id)
        return dic

    def get_dict_from_request(self, request, structure_id):
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
            print(e)
        self.database.cur.close()
        # setting row_factory back to regular touple base requests:
        self.database.con.row_factory = None
        self.database.cur = self.database.con.cursor()
        return dic

    def get_cell_as_dict(self, structure_id):
        """
        Returns a database row as dictionary
        >>> db = StructureTable('./test-data/test.sql')
        >>> cell = db.get_cell_as_dict(16)
        >>> cell == {'Id': 16, 'StructureId': 16, 'a': 7.9492, 'b': 8.9757, 'c': 11.3745, 'alpha': 106.974, 'beta': 91.963, 'gamma': 103.456, 'volume': 750.33}
        True
        """
        request = """select * from cell where StructureId = ?"""
        # setting row_factory to dict for the cif keys:
        dic = self.get_dict_from_request(request, structure_id)
        return dic

    @staticmethod
    def joined_arglist(items):
        """
        Retruns a string of ?, with the length of the input list.
        >>> StructureTable.joined_arglist([1, 2, 3, 'abc', 'def'])
        '?, ?, ?, ?, ?'
        """
        return ', '.join(['?'] * len(items))

    def get_cells_as_list(self, structure_ids: list):
        """
        Returns a list of unit cells from the list of input ids.
        >>> db = StructureTable('./test-data/test.sql')
        >>> db.get_cells_as_list([16])
        [(7.9492, 8.9757, 11.3745, 106.974, 91.963, 103.456, 750.33)]
        """
        req = 'select a, b, c, alpha, beta, gamma, volume from cell where StructureId IN ({seq})'.format(
                seq=self.joined_arglist(structure_ids))
        return self.database.db_request(req, structure_ids)

    def get_cell_by_id(self, structure_id):
        """
        returns the cell of a res file in the db
        >>> db = StructureTable('./test-data/test.sql')
        >>> db.get_cell_by_id(16)
        (7.9492, 8.9757, 11.3745, 106.974, 91.963, 103.456, 750.33)
        """
        if not structure_id:
            return False
        req = '''SELECT a, b, c, alpha, beta, gamma, volume FROM cell WHERE StructureId = ?'''
        cell = self.database.db_request(req, (structure_id,))
        if cell and len(cell) > 0:
            return cell[0]
        else:
            return cell

    def find_by_volume(self, volume, threshold=0.03):
        """
        Searches cells with volume between upper and lower limit. Returns the Id and the unit cell.
        :param threshold: Volume uncertaincy where to search
        :type threshold: float
        :param volume: the unit cell volume
        :type volume: float
        :return: list
        >>> db = StructureTable('./test-data/test.sql')
        >>> db.find_by_volume(3021.9, threshold=0.01)
        [(9, 9.451, 17.881, 18.285, 90.0, 102.054, 90.0, 3021.9), (252, 9.451, 17.881, 18.285, 90.0, 102.054, 90.0, 3021.9), (69, 12.0939, 15.464, 16.854, 90.0, 105.295, 90.0, 3040.4)]
        >>> db.find_by_volume(30021.9, threshold=0.01)
        ()
        """
        upper_limit = float(volume + volume * threshold)
        lower_limit = float(volume - volume * threshold)
        req = '''SELECT StructureId, a, b, c, alpha, beta, gamma, volume FROM cell WHERE cell.volume >= ? AND cell.volume <= ?'''
        try:
            return self.database.db_request(req, (lower_limit, upper_limit))
        except(TypeError, KeyError):
            # print("Wrong volume for cell search.")
            return []

    def find_by_niggli_cell(self, a, b, c, alpha, beta, gamma, axtol=0.02, angtol=0.025, maxsolutions=None):
        """
        Searches cells with certain deviations in the unit cell parameters.
        #>>> db = StructureTable('./test-data/test.sql')
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

    def find_by_strings(self, text):
        """
        Searches cells with volume between upper and lower limit
        :param text: Volume uncertaincy where to search
        id, name, data, path
        >>> db = StructureTable('./test-data/test.sql')
        >>> db.find_by_strings('NTD51a')
        [(237, b'DK_NTD51a-final.cif', b'p21c', b'/Users/daniel/GitHub/StructureFinder/test-data/051a')]
        >>> db.find_by_strings('ntd51A')
        [(237, b'DK_NTD51a-final.cif', b'p21c', b'/Users/daniel/GitHub/StructureFinder/test-data/051a')]
        """
        req = '''
        SELECT StructureId, filename, dataname, path FROM txtsearch WHERE filename MATCH ?
          UNION
        SELECT StructureId, filename, dataname, path FROM txtsearch WHERE dataname MATCH ?
          UNION
        SELECT StructureId, filename, dataname, path FROM txtsearch WHERE path MATCH ?
          UNION
        SELECT StructureId, filename, dataname, path FROM txtsearch WHERE shelx_res_file MATCH ?
        '''
        try:
            res = self.database.db_request(req, (text, text, text, text))
        except (TypeError, ProgrammingError, OperationalError) as e:
            print('DB request error in find_by_strings().', e)
            return tuple([])
        return res

    def find_by_it_number(self, number: int) -> List[int]:
        """
        Find structures by space group number in international tables of
        crystallography.
        Returns a list of index numbers.
        >>> db = StructureTable('./test-data/test.sql')
        >>> db.find_by_it_number(1)
        [33]
        >>> db.find_by_it_number(500)
        []
        """
        try:
            value = int(number)
        except ValueError:
            return []
        req = '''SELECT StructureId from Residuals WHERE _space_group_IT_number IS ?'''
        result = self.database.db_request(req, (value,))
        return self.result_to_list(result)

    def result_to_list(self, result):
        if result and len(result) > 0:
            return [x[0] for x in result]
        else:
            return []

    def find_by_elements(self, elements: list, excluding: list = None, onlyincluded: bool = False) -> list:
        """
        Find structures where certain elements are included in the sum formula.

        >>> db = StructureTable('./test-data/test.sql')
        >>> db.find_by_elements(['S', 'Sn'])
        [75]
        >>> db.find_by_elements(['Sn'])
        [75, 187]
        >>> db.find_by_elements(['Xe'])
        []
        >>> db.find_by_elements(['C', 'H', 'O', 'N', 'Cl'], onlyincluded=True)
        [15, 59, 157, 170, 260]
        >>> db.find_by_elements(['C', 'H', 'O', 'N', 'Cl'], excluding=['Al', 'B', 'S', 'Si', 'Br', 'P'], onlyincluded=False)
        [15, 56, 59, 115, 133, 157, 170, 209, 260]
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

    def find_by_date(self, start='0000-01-01', end='NOW'):
        """
        Find structures between start and end date.

        >>> db = StructureTable('./test-data/test.sql')
        >>> db.find_by_date(start='2017-08-25', end='2018-05-05')
        [16, 17, 20, 21, 241]
        """
        req = """
              SELECT StructureId FROM Residuals WHERE modification_time between DATE(?) AND DATE(?);
              """
        result = self.database.db_request(req, (start, end))
        return self.result_to_list(result)

    def find_by_rvalue(self, rvalue: float):
        """
        Finds structures with R1 value better than rvalue. I search both R1 values, because often one or even both
        are missing.

        >>> db = StructureTable('./test-data/test.sql')
        >>> db.find_by_rvalue(0.035)
        [18, 64, 75, 128, 131, 135, 151, 164, 236, 237, 243]
        """
        req = """
                SELECT StructureId FROM Residuals WHERE _refine_ls_R_factor_gt <= ? OR _refine_ls_R_factor_all <= ?
                """
        return self.result_to_list(self.database.db_request(req, (rvalue, rvalue)))

    def find_biggest_cell(self):
        """
        Finds the structure with the biggest cell in the db. This should be done by volume, but was
        just for fun...
        >>> db = StructureTable('./test-data/test.sql')
        >>> db.find_biggest_cell()
        (250, 48.48, 21.72, 10.74)
        """
        req = '''SELECT Id, a, b, c FROM cell GROUP BY Id ORDER BY a, b, c ASC'''
        result = self.database.db_request(req)
        if result:
            return result[-1]
        else:
            return False

    def get_database_version(self):
        """
        >>> db = StructureTable('./test-data/test.sql')
        >>> db.get_database_version()
        0
        """
        req = """
              SELECT Format FROM database_format;
              """
        try:
            version = self.database.db_request(req)[0][0]
        except IndexError:
            version = 0
        return version

    def set_database_version(self, version=0):
        """
        Database version to indicate apex or other formats. A value of 1 means the data is from APEX.
        >>> db = StructureTable('./test-data/test.sql')
        >>> db.get_database_version()
        0
        """
        req = """
              INSERT or REPLACE into database_format (Id, Format) values (?, ?)
              """
        self.database.db_request(req, (1, version))


if __name__ == '__main__':
    # searcher.filecrawler.put_cifs_in_db(searchpath='../')
    # db = DatabaseRequest('./test3.sqlite')
    # db.initialize_db()
    db = StructureTable(r'C:\Program Files (x86)\CCDC\CellCheckCSD\cell_check.csdsql')
    # db.initialize_db()
    # db = StructureTable('../structurefinder.sqlite')
    # db.database.initialize_db()
    # out = db.find_by_date(start="2017-08-19")
    # out = db.get_cell_by_id(12)
    # out = db.find_by_strings('dk')
    ############################################
    elinclude = ['C', 'O', 'N', 'F']
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
    req = """SELECT Id FROM NORMALISED_REDUCED_CELLS WHERE Volume >= ? AND Volume <= ?"""
    result = db.database.db_request(req, (1473.46, 1564.76))
    print(result)
    # lattice1 = Lattice.from_parameters_niggli_reduced(*cell)
