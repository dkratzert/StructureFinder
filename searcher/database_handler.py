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

from lattice import lattice
from pymatgen.core.lattice import Lattice
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
        self.cur.execute("DROP TABLE IF EXISTS niggli_cell")
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
                        path  TEXT,
                        filename    VARCHAR(255),
                        dataname    VARCHAR(255),
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
                        Name    VARCHAR(255),
                        element    VARCHAR(2),
                        x    FLOAT,
                        y    FLOAT,
                        z    FLOAT,
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
            print(e)
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
        >>> db = FragmentTable(dbfile)
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

    def get_all_structure_names(self):
        """
        returns all fragment names in the database, sorted by name
        """
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
        return self.database.db_request(req, structure_id, measurement_id, filename, path, dataname)

    def fill_measuremnts_table(self, name, structure_id):
        """
        Fills a measurements into the database.

        """
        req = '''
              INSERT INTO measurement (Id, name) VALUES(?, ?)
              '''
        return self.database.db_request(req, structure_id, name)

    def fill_cell_table(self, structure_id, a, b, c, alpha, beta, gamma):
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
        a = a.split('(')[0]
        b = b.split('(')[0]
        c = c.split('(')[0]
        alpha = alpha.split('(')[0]
        beta = beta.split('(')[0]
        gamma = gamma.split('(')[0]
        volume = lattice.vol_unitcell(float(a), float(b), float(c), float(alpha), float(beta), float(gamma))
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

    def find_cell_by_abc(self, a=False, b=False, c=False):
        """
        finds a cell
        """
        if a and not b and not c:    
            req = '''SELECT * FROM cell WHERE cell.a GLOB '{0}*' 
                    '''.format(a)
        elif b and not a and not  c:    
            req = '''SELECT * FROM cell WHERE cell.b GLOB '{0}*' 
                    '''.format(b)
        elif c and not a and not b:    
            req = '''SELECT * FROM cell WHERE cell.c GLOB '{0}*' 
                    '''.format(c)
        elif a and b and not c:    
            req = '''SELECT * FROM cell WHERE cell.a GLOB '{0}*' AND 
                                              cell.b GLOB '{1}*'
                    '''.format(a, b)
        elif a and c and not b:
            req = '''SELECT * FROM cell WHERE cell.a GLOB '{0}*' AND 
                                              cell.c GLOB '{1}*'
                    '''.format(a, c)
        elif b and c and not a:
            req = '''SELECT * FROM cell WHERE cell.b GLOB '{0}*' AND 
                                              cell.c GLOB '{1}*'
                    '''.format(b, c)    
        elif a and b and c:
            req = '''SELECT * FROM cell WHERE 
                    cell.a GLOB '{0}*' AND 
                    cell.b GLOB '{1}*' AND 
                    cell.c GLOB '{2}*'    '''.format(a, b, c)
        else:
            print('wrong search request: a={}, b={}, c={}'.format(a, b, c))
            sys.exit()
        return self.database.db_request(req)

    def find_by_volume(self, volume):
        """
        Searches cells with volume between upper and lower limit
        :param volume: the unit cell volume
        :type volume: float
        :return: list
        """
        upper_limit = volume+volume*0.05
        lower_limit = volume + volume * 0.05
        req = '''SELECT StructureId FROM cell WHERE cell.volume >= '{0}' AND cell.volume <= '{1}'  
                            '''.format(lower_limit, upper_limit)
        return self.database.db_request(req)

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
    res = s.find_by_volume(500)
    print(res)
    #latt = Lattice.from_string("10 20 30 90 91 92")
    #for x in range(1000):
    #    cell = s.get_cell_by_id(2)[0]
    #    #print(cell)
    #    m = latt.find_mapping(Lattice.from_parameters(*cell))
    #    #print(m)
    #print("ready")

