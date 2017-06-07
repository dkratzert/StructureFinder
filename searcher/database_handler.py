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
from pprint import pprint

import searcher
from lattice import lattice
from searcher import misc
from searcher.misc import get_error_from_value

__metaclass__ = type  # use new-style classes
import sqlite3
from sqlite3 import OperationalError


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
        self.cur.execute("DROP TABLE IF EXISTS structure")
        self.cur.execute("DROP TABLE IF EXISTS measurement")
        self.cur.execute("DROP TABLE IF EXISTS cell")
        self.cur.execute("DROP TABLE IF EXISTS Atoms")
        self.cur.execute("DROP TABLE IF EXISTS niggli_cell")
        self.cur.execute("DROP TABLE IF EXISTS Residuals")
        try:
            self.cur.execute("DROP INDEX cell")
        except:
            pass
        try:
            self.cur.execute("DROP INDEX path")
        except:
            pass
        try:
            self.cur.execute("DROP INDEX name")
        except:
            pass

        self.cur.execute('''
                    CREATE TABLE measurement (
                        Id    INTEGER NOT NULL,
                        name    VARCHAR(255),
                        PRIMARY KEY(Id));
                    ''')

        self.cur.execute('''
                    CREATE TABLE Structure (
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
                    CREATE TABLE Atoms (
                        Id    INTEGER NOT NULL,
                        StructureId    INTEGER NOT NULL,
                        Name       TEXT,
                        element    TEXT,
                        x          FLOAT,
                        y          FLOAT,
                        z          FLOAT,
                    PRIMARY KEY(Id),
                      FOREIGN KEY(StructureId)
                        REFERENCES Structure(Id)
                          ON DELETE CASCADE
                          ON UPDATE NO ACTION);
                    ''')

        self.cur.execute('''
                    CREATE TABLE Residuals (
                        Id    INTEGER NOT NULL,
                        StructureId         INTEGER NOT NULL,
                        _cell_formula_units_Z           INTEGER,
                        _space_group_name_H_M_alt       TEXT,
                        _space_group_name_Hall          TEXT,
                        _space_group_IT_number          REAL,
                        _space_group_crystal_system     TEXT,
                        _audit_creation_method          TEXT,
                        _chemical_formula_sum           TEXT,
                        _chemical_formula_weight        TEXT,
                        _exptl_crystal_description      TEXT,
                        _exptl_crystal_colour           TEXT,
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
                        number_of_atoms                         INTEGER,
                    PRIMARY KEY(Id),
                      FOREIGN KEY(StructureId)
                        REFERENCES Structure(Id)
                          ON DELETE CASCADE
                          ON UPDATE NO ACTION);
                    ''')

        self.cur.execute(
                    '''
                    CREATE TABLE cell (
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
                    CREATE TABLE niggli_cell (
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
        
    def db_fetchone(self, request):
        """
        fetches one db entry
        """
        self.cur.execute(request)
        row = self.cur.fetchone()
        return row

    def db_request(self, request, *args):
        """
        Performs a SQLite3 database request with "request" and optional arguments
        to insert parameters via "?" into the database request.
        A push request will return the last row-Id.
        A pull request will return the requested rows
        :param request: sqlite database request like:
                    '''SELECT Structure.cell FROM Structure'''
        :type request: str
        """
        # print('-'*30, 'start')
        # print('request:', request)
        # print('args:', args)
        # print('_' * 30, 'end')
        try:
            if isinstance(args[0], (list, tuple)):
                args = args[0]
        except IndexError:
            pass
        try:
            self.cur.execute(request, args)
            last_rowid = self.cur.lastrowid
        except OperationalError as e:
            print(e, "\nDB execution error")
            return False
        rows = self.cur.fetchall()
        if not rows:
            return last_rowid
        else:
            return rows

    def __del__(self):
        # commit is very slow:
        self.con.commit()
        self.con.close()

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

    def get_all_structure_names(self, ids=None):
        """
        returns all fragment names in the database, sorted by name
        """
        if ids:
            req = '''SELECT Structure.Id, Structure.measurement, Structure.path, Structure.filename, 
                         Structure.dataname FROM Structure WHERE Structure.Id in {}'''.format(tuple(ids))
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
        req_path = '''SELECT Structure.name, Structure.path FROM Structure WHERE
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
        cell = self.database.db_request(req)[0]
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
        req = '''SELECT Id FROM {0} WHERE {1}.Id = {2}'''.format(table, table, Id)
        if self.database.db_request(req):
            return True

    def fill_structures_table(self, path, filename, structure_id, measurement_id, dataname):
        """
        Fills a structure into the database.
        
        """
        req = '''
              INSERT INTO Structure (Id, measurement, filename, path, dataname) VALUES(?, ?, ?, ?, ?)
              '''
        filename = filename.encode("utf-8", "surrogateescape")
        path = path.encode("utf-8", "surrogateescape")
        dataname = dataname.encode("utf-8", "surrogateescape")
        return self.database.db_request(req, structure_id, measurement_id, filename, path, dataname)

    def fill_measuremnts_table(self, name, structure_id):
        """
        Fills a measurements into the database.

        """
        req = '''
              INSERT INTO measurement (Id, name) VALUES(?, ?)
              '''
        name = name.encode("utf-8", "surrogateescape")
        return self.database.db_request(req, structure_id, name)

    def fill_cell_table(self, structure_id, a, b, c, alpha, beta, gamma):
        """
        fill the cell of structure(structureId) in the table
        cell = [a, b, c, alpha, beta, gamma]
        """
        # TODO: Only calc volume if not in cif:
        req = '''INSERT INTO cell (StructureId, a, b, c, alpha, beta, gamma, 
                                   esda, esdb, esdc, esdalpha, esdbeta, esdgamma, volume) 
                            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        aerror = get_error_from_value(a)
        berror = get_error_from_value(b)
        cerror = get_error_from_value(c)
        alphaerror = get_error_from_value(alpha)
        betaerror = get_error_from_value(beta)
        gammaerror = get_error_from_value(gamma)
        a = a.split('(')[0]
        b = b.split('(')[0]
        c = c.split('(')[0]
        alpha = alpha.split('(')[0]
        beta = beta.split('(')[0]
        gamma = gamma.split('(')[0]
        volume = 0.0
        try:
            volume = lattice.vol_unitcell(float(a), float(b), float(c), float(alpha), float(beta), float(gamma))
        except ValueError:
            print(a, b, c, alpha, beta, gamma)
        if self.database.db_request(req, structure_id, a, b, c, alpha, beta, gamma,
                                    aerror, berror, cerror, alphaerror, betaerror, gammaerror, volume):
            return True

    def fill_atoms_table(self, structure_id, name, element, x, y, z):
        """
        fill the atoms into structure(structureId) 
        :TODO: Add bonds?
        """
        req = '''INSERT INTO Atoms (StructureId, name, element, x, y, z) VALUES(?, ?, ?, ?, ?, ?)'''
        if self.database.db_request(req, structure_id, name, element, x, y, z):
            return True

    def fill_residuals_table(self, structure_id, data):
        """
        Fill the table with residuals of the refinement.

        c.execute('CREATE TABLE {tn} ({nf} {ft} PRIMARY KEY)'\
        .format(tn=table_name2, nf=new_field, ft=field_type))
        http://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html
        # A) Adding a new column without a row value
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
        .format(tn=table_name, cn=new_column1, ct=column_type))

        :param structure_id:
        :param param:
        :return:
        """
        result = False
        print(data, structure_id)
        for i in data:
            req = '''INSERT INTO Residuals (StructureId, {}) VALUES(?, ?)'''.format(i)
            result = self.database.db_request(req, [structure_id, data[i]])
        if result:
            return True
        else:
            print('Failed to insert residuel {}'.format(i))
            return False

    def clean_name(some_var):
        """
        Make shure only alphanumerical characters are in the name
        :type some_var: str
        :rtype: str
        """
        return ''.join(char for char in some_var if char.isalnum())

    def find_by_volume(self, volume, threshold = 0.03):
        """
        Searches cells with volume between upper and lower limit
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
    s = StructureTable("../test.sqlite")
    #vol = lattice.vol_unitcell(8.4009,  10.4848,  11.8979,  94.7910, 103.0250, 108.5480) # 954
    # 8.40 10.48 11.99 94.78 103.0 108.55
    vol = lattice.vol_unitcell(8.4, 10.5, 11.9, 95, 103, 109)  # 952
    print(vol)
    res = s.find_by_volume(vol)
    print(res)
    #latt = Lattice.from_string("10 20 30 90 91 92")
    #for x in range(1000):
    #    cell = s.get_cell_by_id(2)[0]
    #    #print(cell)
    #    m = latt.find_mapping(Lattice.from_parameters(*cell))
    #    #print(m)
    #print("ready")

