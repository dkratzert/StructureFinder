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

import sqlite3
import sys
from sqlite3 import OperationalError

import numpy as np

import searcher
from lattice import lattice
from searcher import misc
from searcher.constants import py36
from searcher.misc import get_error_from_value

__metaclass__ = type  # use new-style classes


class DatabaseRequest():
    def __init__(self, dbfile):
        """
        creates a connection and the cursor to the SQLite3 database file "dbfile".
        :param dbfile: database file
        :type dbfile: str
        """
        # open the database
        self.con = sqlite3.connect(dbfile)
        self.con.execute("PRAGMA foreign_keys = ON")
        self.con.text_factory = str
        #self.con.text_factory = bytes
        with self.con:
            # set the database cursor
            self.cur = self.con.cursor()

    def initialize_db(self):
        """
        initializtes the db
        """
        #self.con.execute("PRAGMA foreign_keys = ON")
        #self.cur.execute("DROP TABLE IF EXISTS structure")
        ##self.cur.execute("DROP TABLE IF EXISTS measurement")
        #self.cur.execute("DROP TABLE IF EXISTS cell")
        #self.cur.execute("DROP TABLE IF EXISTS Atoms")
        #self.cur.execute("DROP TABLE IF EXISTS niggli_cell")
        #self.cur.execute("DROP TABLE IF EXISTS Residuals")
        self.cur.execute("DROP TABLE IF EXISTS txtsearch")
        self.cur.execute("DROP TABLE IF EXISTS ElementSearch")

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
                    PRIMARY KEY(Id),
                      FOREIGN KEY(StructureId)
                        REFERENCES Structure(Id)
                          ON DELETE CASCADE
                          ON UPDATE NO ACTION);
                    ''')
        if py36:
            # The simple tokenizer is best for my purposes:
            self.cur.execute("""
                CREATE VIRTUAL TABLE txtsearch USING 
                        fts4(StructureId    INTEGER, 
                             filename       TEXT, 
                             dataname       TEXT, 
                             path           TEXT,
                             shelx_res_file TEXT,
                                tokenize=simple "tokenchars= .=-_");  
            """)
            # Now the table for element search:
            self.cur.execute("""
                CREATE VIRTUAL TABLE ElementSearch USING
                        fts4(StructureId        INTEGER,
                        _chemical_formula_sum   TEXT,
                            tokenize=simple 'tokenchars= 0123456789');
            """)

        self.cur.execute('''
                    CREATE TABLE IF NOT EXISTS Residuals (
                        Id                                      INTEGER NOT NULL,
                        StructureId                             INTEGER NOT NULL,
                        _cell_formula_units_Z                   INTEGER,
                        _space_group_name_H_M_alt               TEXT,
                        _space_group_name_Hall                  TEXT,
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
                        _reflns_number_total 					REAL,
                        _reflns_number_gt 					    REAL,
                        _reflns_threshold_expression 			TEXT,
                        _reflns_Friedel_coverage 				REAL,
                        _computing_structure_solution 			TEXT,
                        _computing_structure_refinement 		TEXT,
                        _refine_special_details 				TEXT,
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
                        esda    FLOAT,
                        esdb    FLOAT,
                        esdc    FLOAT,
                        esdalpha   FLOAT,
                        esdbeta    FLOAT,
                        esdgamma   FLOAT,
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
                            PRIMARY KEY(Id),
                              FOREIGN KEY(StructureId)
                                REFERENCES niggli_cell(Id)
                                  ON DELETE CASCADE
                                  ON UPDATE NO ACTION);
                    '''
                    )

    def get_lastrowid(self):
        """
        Retrurns the last rowid of a loaded database.

        >>> db = DatabaseRequest('test.sqlite')
        >>> db.get_lastrowid()
        """
        lastid = self.db_fetchone("""SELECT max(id) FROM Structure""")
        try:
            return lastid[0]
        except TypeError:
            # No database or empty table:
            return 0


    def db_fetchone(self, request):
        """
        fetches one db entry
        """
        try:
            self.cur.execute(request)
        except OperationalError:
            return False
        row = self.cur.fetchone()
        return row

    def db_request(self, request, *args, many=False):
        """
        Performs a SQLite3 database request with "request" and optional arguments
        to insert parameters via "?" into the database request.
        A push request will return the last row-Id.
        A pull request will return the requested rows
        :param request: sqlite database request like:
                    '''SELECT Structure.cell FROM Structure'''
        :type request: str
        """
        #print('-'*30, 'start')
        #print('request:', request)
        #print('args:', args)
        #print('_' * 30, 'end')
        try:
            if isinstance(args[0], (list, tuple)):
                args = args[0]
        except IndexError:
            pass
        try:
            if many:
                #print(args[0])
                self.cur.executemany(request, args)
            else:
                self.cur.execute(request, args)
            last_rowid = self.cur.lastrowid
        except OperationalError as e:
            print(e, "\nDB execution error")
            return False
        rows = self.cur.fetchall()
        if not rows:
            return tuple()
            #return last_rowid
        else:
            return rows

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def __del__(self):
        # commit is very slow:
        try:
            self.con.commit()
        except sqlite3.ProgrammingError:
            pass
        try:
            self.con.close()
        except sqlite3.ProgrammingError:
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
        self.database = DatabaseRequest(dbfile)

    def __len__(self):
        """
        Called to implement the built-in function len().
        Should return the number of database entrys.
        
        :rtype: int
        """
        req = '''SELECT Structure.Id FROM Structure'''
        rows = self.database.db_request(req)
        if rows:
            return len(rows)
        else:
            return False
            #raise IndexError('Could not determine database size')

    def __getitem__(self, str_id):
        try:
            str_id = int(str_id)
        except(ValueError, KeyError):
            print('Wrong type. Integer expected')
            sys.exit()
        if str_id < 0:
            str_id = len(self)-abs(str_id)
        found = self.get_filepath(str_id)
        if found:
            return found
        #else:
        #    raise IndexError('Database entry not found.')

    def __iter__(self):
        """
        This method is called when an iterator is required for FragmentTable.
        Returns the Id and the Name as tuple.
  
        >>> dbfile = 'test-data/test.sqlite'
        >>> db = StructureTable(dbfile)
        >>> for num, i in enumerate(db):
        ...   print(i)
        ...   if num > 1:
        ...     break
        """
        all_structures = self.get_all_structure_names()
        if all_structures:
            return iter(all_structures)
        else:
            return False

    def get_all_structure_names(self, ids: list = None) -> list:
        """
        returns all fragment names in the database, sorted by name
        :returns [id, meas, path, filename, data]
        """
        if ids:
            if len(ids) > 1:
                ids = tuple(ids)
                req = '''SELECT Structure.Id, Structure.measurement, Structure.path, Structure.filename, 
                         Structure.dataname FROM Structure WHERE Structure.Id in {}'''.format(ids)
            else:
                req = '''SELECT Structure.Id, Structure.measurement, Structure.path, Structure.filename, 
                            Structure.dataname FROM Structure WHERE Structure.Id == ?'''
                rows = [list(i) for i in self.database.db_request(req, ids[0])]
                return rows
        else:
            req = '''SELECT Structure.Id, Structure.measurement, Structure.path, Structure.filename, 
                                     Structure.dataname FROM Structure'''
        try:
            rows = [list(i) for i in self.database.db_request(req)]
        except TypeError:
            return []
        return rows

    def get_filepath(self, structure_id):
        """
        returns the path of a res file in the db
        """
        req_path = '''SELECT Structure.dataname, Structure.path FROM Structure WHERE
            Structure.Id = {0}'''.format(structure_id)
        path = self.database.db_request(req_path)[0]
        return path

    def get_cell_by_id(self, structure_id):
        """
        returns the cell of a res file in the db
        """
        if not structure_id:
            return False
        req = '''SELECT a, b, c, alpha, beta, gamma, volume FROM cell WHERE StructureId = {0}'''.format(structure_id)
        cell = self.database.db_request(req)
        if cell and len(cell) > 0:
            return cell[0]
        else:
            return cell

    def __contains__(self, str_id):
        """
        return if db contains entry of id
        """
        try:
            str_id = int(str_id)
        except(ValueError, TypeError):
            print('Wrong type. Expected integer.')
        if self.has_index(str_id):
            return True
        else:
            return False

    def has_index(self, Id, table='Structure'):
        """
        Returns True if db has index Id
        :param table: which db table to query
        :type table: str
        :param Id: Id of the respective cell
        :type Id: int
        :rtype: bool
        """
        req = '''SELECT Id FROM ? WHERE ?.Id = ?'''
        if self.database.db_request(req, (table, table, Id)):
            return True

    def fill_structures_table(self, path, filename, structure_id, measurement_id, dataname):
        """
        Fills a structure into the database.
        
        """
        req = '''
              INSERT INTO Structure (Id, measurement, filename, path, dataname) VALUES(?, ?, ?, ?, ?)
              '''
        filename = filename.encode("utf-8", "ignore")#.encode("utf-8", "surrogateescape")
        path = path.encode("utf-8", "ignore")
        dataname = dataname.encode("utf-8", "ignore")
        self.database.db_request(req, structure_id, measurement_id, filename, path, dataname)
        return structure_id

    def fill_measuremnts_table(self, name, structure_id):
        """
        Fills a measurements into the database.

        """
        req = '''
              INSERT INTO measurement (Id, name) VALUES(?, ?)
              '''
        name = name.encode("utf-8", "surrogateescape")
        self.database.db_request(req, structure_id, name)
        return structure_id

    def fill_cell_table(self, structure_id, a, b, c, alpha, beta, gamma, volume):
        """
        fill the cell of structure(structureId) in the table
        cell = [a, b, c, alpha, beta, gamma]
        """
        req = '''INSERT INTO cell (StructureId, a, b, c, alpha, beta, gamma, 
                                   esda, esdb, esdc, esdalpha, esdbeta, esdgamma, volume) 
                            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        aerror = get_error_from_value(a)
        berror = get_error_from_value(b)
        cerror = get_error_from_value(c)
        alphaerror = get_error_from_value(alpha)
        betaerror = get_error_from_value(beta)
        gammaerror = get_error_from_value(gamma)
        vol = ''
        if isinstance(a, str):
            a = a.split('(')[0]
            b = b.split('(')[0]
            c = c.split('(')[0]
            alpha = alpha.split('(')[0]
            beta = beta.split('(')[0]
            gamma = gamma.split('(')[0]
        if isinstance(volume, str):
            vol = volume.split('(')[0]
        if self.database.db_request(req, structure_id, a, b, c, alpha, beta, gamma,
                                    aerror, berror, cerror, alphaerror, betaerror, gammaerror, vol):
            return True

    def fill_atoms_table(self, structure_id, name, element, x, y, z, occ, part):
        """
        fill the atoms into structure(structureId) 
        :TODO: Add bonds?
        """
        req = '''INSERT INTO Atoms (StructureId, name, element, x, y, z, occupancy, part) 
                                    VALUES(?, ?, ?, ?, ?, ?, ?, ?)'''
        if self.database.db_request(req, structure_id, name, element, x, y, z, occ, part):
            return True

    def get_atoms_table(self, structure_id, cell='', cartesian=False):
        """
        returns the atoms of structure with structure_id
        """
        req = """SELECT Name, element, x, y, z FROM Atoms WHERE StructureId = ?"""
        result = self.database.db_request(req, structure_id)
        if cartesian:
            cartesian_coords = []
            a = lattice.A(cell).orthogonal_matrix
            for at in result:
                coord = np.matrix([at[2], at[3], at[4]])
                coords = misc.flatten((a * coord.reshape(3, 1)).tolist())
                cartesian_coords.append(list(at[:2])+coords)
            return cartesian_coords
        if result:
            return result
        else:
            return False

    def get_residuals(self, structure_id, residual):
        """
        Get the value of a single residual from the residuals table.
        """
        if not structure_id:
            return False
        req = '''SELECT ? FROM Residuals WHERE StructureId = ?'''
        try:
            res = self.database.db_request(req, (residual, structure_id))[0][0]
        except TypeError:
            res = '?'
        return res

    def fill_residuals_table(self, structure_id, cif):
        """
        Fill the table with residuals of the refinement.

        c.execute('CREATE TABLE {tn} ({nf} {ft} PRIMARY KEY)'\
        .format(tn=table_name2, nf=new_field, ft=field_type))
        http://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html
        # A) Adding a new column without a row value
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
        .format(tn=table_name, cn=new_column1, ct=column_type))

        intab = "aeiou"
        outtab = "12345"
        trantab = maketrans(intab, outtab)

        str = "this is string example....wow!!!";
        print str.translate(trantab)
        :param cif:
        :param structure_id:
        :param param:
        :return:
        """
        req = '''INSERT INTO Residuals 
                    (
                    StructureId,
                    _cell_formula_units_Z,                  
                    _space_group_name_H_M_alt,  
                    _space_group_name_Hall,
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
                    _shelx_res_file
                    ) 
                VALUES
                    (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    );
                '''
        result = self.database.db_request(req,
                structure_id,
                cif.cif_data['_cell_formula_units_Z'],              # Z
                cif.cif_data['_space_group_name_H-M_alt'],          # Raumgruppe (Herman-Maugin)
                cif.cif_data['_space_group_name_Hall'],             # Hall-Symbol
                cif.cif_data['_space_group_IT_number'],             # Raumgruppen-Nummer aus IT
                cif.cif_data['_space_group_crystal_system'],        # Kristallsystem
                cif.cif_data['_space_group_symop_operation_xyz'],   # SYMM cards
                cif.cif_data['_chemical_formula_sum'],              # Summenformel
                cif.cif_data['_chemical_formula_weight'],           # Moyety-Formel
                cif.cif_data['_exptl_crystal_description'],         # Habitus
                cif.cif_data['_exptl_crystal_colour'],              # Farbe
                cif.cif_data['_exptl_crystal_size_max'],            # Größe
                cif.cif_data['_exptl_crystal_size_mid'],            # Größe
                cif.cif_data['_exptl_crystal_size_min'],            # Größe
                cif.cif_data['_audit_creation_method'],             # how data were entered into the data block.
                cif.cif_data['_exptl_absorpt_coefficient_mu'],      # Linear absorption coefficient (mm-1)
                cif.cif_data['_exptl_absorpt_correction_type'],     # Code for absorption correction
                cif.cif_data['_diffrn_ambient_temperature'],        # The mean temperature in kelvins at which the
                                                                    # intensities were measured.
                cif.cif_data['_diffrn_radiation_wavelength'],       # Radiation wavelength (Å)
                cif.cif_data['_diffrn_radiation_type'],             # Radiation type (e.g. neutron or `Mo Kα')
                cif.cif_data['_diffrn_source'],                     # Röntgenquelle
                cif.cif_data['_diffrn_measurement_device_type'],    # Diffractometer make and type
                cif.cif_data['_diffrn_reflns_number'],              # Total number of reflections measured excluding systematic absences
                cif.cif_data['_diffrn_reflns_av_R_equivalents'],    # R(int) -> R factor for symmetry-equivalent intensities
                cif.cif_data['_diffrn_reflns_theta_min'],           # Minimum θ of measured reflections (°)
                cif.cif_data['_diffrn_reflns_theta_max'],           # Maximum θ of measured reflections (°)
                cif.cif_data['_diffrn_reflns_theta_full'],          # θ to which available reflections are close to 100% complete (°)
                cif.cif_data['_diffrn_measured_fraction_theta_max'],   # completeness, Fraction of unique reflections measured to θmax
                cif.cif_data['_diffrn_measured_fraction_theta_full'],  # Fraction of unique reflections measured to θfull
                cif.cif_data['_reflns_number_total'],               # Number of symmetry-independent reflections excluding
                                                                    # systematic absences.
                cif.cif_data['_reflns_number_gt'],                  # Number of reflections > σ threshold
                cif.cif_data['_reflns_threshold_expression'],       # σ expression for F, F2 or I threshold
                cif.cif_data['_reflns_Friedel_coverage'],           # The proportion of Friedel-related reflections
                                                                    # present in the number of reported unique reflections
                cif.cif_data['_computing_structure_solution'],      # Reference to structure-solution software
                cif.cif_data['_computing_structure_refinement'],    # Reference to structure-refinement software
                cif.cif_data['_refine_special_details'],            # Details about the refinement
                cif.cif_data['_refine_ls_structure_factor_coef'],   # Code for F, F2 or I used in least-squares refinement
                cif.cif_data['_refine_ls_weighting_details'],       # Weighting expression
                cif.cif_data['_refine_ls_number_reflns'],           # Number of reflections used in refinement
                cif.cif_data['_refine_ls_number_parameters'],       # Number of parameters refined
                cif.cif_data['_refine_ls_number_restraints'],       # Number of restraints applied during refinement
                cif.cif_data['_refine_ls_R_factor_all'],
                cif.cif_data['_refine_ls_R_factor_gt'],             # R1 factor of F for reflections > threshold
                cif.cif_data['_refine_ls_wR_factor_ref'],           # wR2 factor of coefficient for refinement reflections
                cif.cif_data['_refine_ls_wR_factor_gt'],
                cif.cif_data['_refine_ls_goodness_of_fit_ref'],     # Goodness of fit S for refinement reflections
                cif.cif_data['_refine_ls_restrained_S_all'],        # The least-squares goodness-of-fit parameter S' for
                                                                    # all reflections after the final cycle of least-squares refinement.
                cif.cif_data['_refine_ls_shift/su_max'],            # Maximum shift/s.u. ratio after final refinement cycle
                cif.cif_data['_refine_ls_shift/su_mean'],
                cif.cif_data['_refine_diff_density_max'],           # Maximum difference density after refinement
                cif.cif_data['_refine_diff_density_min'],           # Deepest hole
                cif.cif_data['_diffrn_reflns_av_unetI/netI'],       # R(sigma)
                cif.cif_data['_database_code_depnum_ccdc_archive'],  # CCDC number
                cif.cif_data['_shelx_res_file']                      # The content of the SHELXL res file
                )
        return result

    def clean_name(some_var):
        """
        Make sure only alphanumerical characters are in the name
        :type some_var: str
        :rtype: str
        """
        return ''.join(char for char in some_var if char.isalnum())

    def populate_fulltext_search_table(self):
        """
        Populates the fts4 table with data to search for text.
        _publ_contact_author_name
        TODO: merge with residuals
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
                        INNER JOIN Residuals AS res WHERE str.Id = res.Id;
        """
        optimize_queries = """INSERT INTO txtsearch(txtsearch) VALUES('optimize');"""
        element_search = """
            INSERT INTO ElementSearch(StructureId,
                                    _chemical_formula_sum) 
                SELECT Id, _chemical_formula_sum FROM residuals; 
        """
        if py36:
            self.database.cur.execute(populate_index)
            self.database.cur.execute(optimize_queries)
            self.database.cur.execute(element_search)

    def get_row_as_dict(self, request):
        """
        Returns a database row as dictionary
        """
        # setting row_factory to dict for the cif keys:
        self.database.con.row_factory = self.database.dict_factory
        self.database.cur = self.database.con.cursor()
        dic = self.database.db_fetchone(request)
        self.database.cur.close()
        # setting row_factory back to regular touple base requests:
        self.database.con.row_factory = None
        self.database.cur = self.database.con.cursor()
        return dic

    def find_by_volume(self, volume, threshold=0.03):
        """
        Searches cells with volume between upper and lower limit
        :param threshold: Volume uncertaincy where to search
        :type threshold: float
        :param volume: the unit cell volume
        :type volume: float
        :return: list
        """
        upper_limit = volume + volume * threshold
        lower_limit = volume - volume * threshold
        req = '''SELECT StructureId FROM cell WHERE cell.volume >= '{0}' AND cell.volume <= '{1}'  
                            '''.format(lower_limit, upper_limit)
        try:
            return searcher.misc.flatten([list(x) for x in self.database.db_request(req)])
        except TypeError:
            return False

    def find_by_strings(self, text: str) -> tuple:
        """
        Searches cells with volume between upper and lower limit
        :param text: Volume uncertaincy where to search
        id, name, data, path
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
            ids = self.database.db_request(req, text, text, text, text)
        except (TypeError, sqlite3.ProgrammingError, sqlite3.OperationalError) as e:
            print('DB request error.', e)
            return tuple([])
        return ids

    def find_by_elements(self, elements: list, anyresult: bool = False) -> list:
        """
        Find structures where certain elements are included in the sum formula.

        >>> db = StructureTable('../structuredb.sqlite')
        >>> db.database.initialize_db()
        >>> db.find_by_elements(['Al', 'ca'])
        {11, 3, 6, 15}
        """
        import re
        structures = []
        matches = []
        req = '''SELECT StructureId, _chemical_formula_sum from ElementSearch WHERE _chemical_formula_sum MATCH ?'''
        for el in elements:
            result = self.database.db_request(req, el+'*')
            if result:
                if isinstance(result, int):
                    continue
                else:
                    structures.extend(result)
        for el in elements:  # The second search excludes false hits like Ca instead of C
            regex = re.compile(r'[\d|\s]?' + el + r'[\d|\s]*', re.IGNORECASE)
            res = []
            for num, form in structures:
                if regex.search(form):
                    res.append(num)
            matches.append(res)
        if matches:
            if anyresult:
                return set(misc.flatten(matches))
            else:
                return set(matches[0]).intersection(*matches)
        else:
            return set()

    def find_biggest_cell(self):
        """
        finds the structure with the biggest cell in the db
        """
        #req = '''SELECT max(a), max(b), max(c) FROM cell'''
        biggest = []
        req = '''SELECT Id, a, b, c FROM cell GROUP BY Id ORDER BY a, b, c ASC'''#.format(edge)
        result = self.database.db_request(req)
        if result:
            return result[-1]
        else:
            return False
                  
            
            
if __name__ == '__main__':
    #searcher.filecrawler.put_cifs_in_db(searchpath='../')
    db = DatabaseRequest('./structuredb.sqlite')
#    db.database.initialize_db()
    out = db.get_lastrowid()
    print(out)

