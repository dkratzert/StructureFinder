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
from datetime import date
from operator import not_

from sqlalchemy import Column, Integer, String, ForeignKey, Float, Date, inspect, TypeDecorator, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import cast

import sqlite3
import sys
from sqlite3 import OperationalError

import searcher
from lattice import lattice
from searcher import misc
from searcher.fileparser import Cif
from searcher.misc import get_error_from_value
from shelxfile.dsrmath import Array

#db_enoding = 'ISO-8859-15'
db_enoding = 'utf-8'

Base = declarative_base()


from sqlalchemy import inspect


def as_dict(row) -> dict:
    """
    Returns the content of a specific table row as dictionary.
    """
    return dict((col, getattr(row, col)) for col in row.__table__.columns.keys())


class CastToIntType(TypeDecorator):
    '''
    Converts stored values to int via CAST operation
    '''
    impl = Numeric

    def column_expression(self, col):
        return cast(col, Integer)


class MyFloat(TypeDecorator):
    '''
    Converts string to float or empty field if sting is empty.
    '''

    impl = Float

    def process_bind_param(self, value, dialect):
        try:
            if isinstance(value, float):
                return value
            val = float(value.split('(')[0])
        except ValueError:
            return None
        return val


class DBFormat(Base):
     __tablename__ = 'database_format'

     id = Column(Integer, primary_key=True)
     format = Column(String)

     def __repr__(self):
        return "<DBFormat(id={0}, format={1})>".format(self.id, self.format)


class Measurement(Base):
    '''
    CREATE TABLE IF NOT EXISTS measurement (
        Id    INTEGER NOT NULL,
        name    VARCHAR(255),
        PRIMARY KEY(Id));

    This is unused and probably never will be.
    '''
    __tablename__ = 'measurement'

    Id = Column(Integer, primary_key=True, nullable=True, unique=False)
    name = Column(String)


class Structure(Base):
    '''
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
    '''
    __tablename__ = 'Structure'

    Id = Column(Integer, primary_key=True)
    measurement = Column(Integer, ForeignKey(Measurement.Id), nullable=True, unique=False)
    path = Column(String)
    filename = Column(String)
    dataname = Column(String)

    def __repr__(self):
        return "<Structure: (id={0}, measurement={1}, path={1}, filename={1}, dataname={1})>"\
            .format(self.id, self.measurement, self.path, self.filename, self.dataname)

class Atoms(Base):
    '''
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
    '''
    __tablename__ = 'Atoms'

    Id = Column(Integer, primary_key=True)
    StructureId = Column(Integer, ForeignKey(Structure.Id))
    Name = Column(String)
    element = Column(String)
    x = Column(MyFloat)
    y = Column(MyFloat)
    z = Column(MyFloat)
    occupancy = Column(Float)
    part = Column(CastToIntType)

    def __repr__(self):
        return '<Atom: {}, {}, {}, {}, {}, {}, {}, {}, {}>'.format(self.Id, self.StructureId, self.Name, self.element,
                                                                   self.x, self.y, self.z, self.occupancy, self.part)


class Residuals(Base):
    '''
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
        _reflns_number_total 					INTEGER,
        _reflns_number_gt 					    INTEGER,
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
        modification_time                       DATE,
        file_size                               INTEGER,
    PRIMARY KEY(Id),
      FOREIGN KEY(StructureId)
        REFERENCES Structure(Id)
          ON DELETE CASCADE
          ON UPDATE NO ACTION);
    '''
    __tablename__ = 'Residuals'

    Id = Column(Integer, primary_key=True)
    StructureId = Column(Integer, ForeignKey(Structure.Id))
    _cell_formula_units_Z = Column(Integer)
    _space_group_name_H_M_alt = Column(String)
    _space_group_name_Hall = Column(String)
    _space_group_IT_number = Column(Integer)
    _space_group_crystal_system = Column(String)
    _space_group_symop_operation_xyz = Column(String)
    _audit_creation_method = Column(String)
    _chemical_formula_sum = Column(String)
    _chemical_formula_weight = Column(String)
    _exptl_crystal_description = Column(String)
    _exptl_crystal_colour = Column(String)
    _exptl_crystal_size_max = Column(MyFloat)
    _exptl_crystal_size_mid = Column(MyFloat)
    _exptl_crystal_size_min = Column(MyFloat)
    _exptl_absorpt_coefficient_mu = Column(MyFloat)
    _exptl_absorpt_correction_type = Column(String)
    _diffrn_ambient_temperature = Column(MyFloat)
    _diffrn_radiation_wavelength = Column(MyFloat)
    _diffrn_radiation_type = Column(String)
    _diffrn_source = Column(String)
    _diffrn_measurement_device_type = Column(String)
    _diffrn_reflns_number = Column(Integer)
    _diffrn_reflns_av_R_equivalents = Column(Integer)
    _diffrn_reflns_theta_min = Column(MyFloat)
    _diffrn_reflns_theta_max = Column(MyFloat)
    _diffrn_reflns_theta_full = Column(MyFloat)
    _diffrn_measured_fraction_theta_max = Column(MyFloat)
    _diffrn_measured_fraction_theta_full = Column(MyFloat)
    _reflns_number_total = Column(Integer)
    _reflns_number_gt = Column(Integer)
    _reflns_threshold_expression = Column(String)
    _reflns_Friedel_coverage = Column(MyFloat)
    _computing_structure_solution = Column(String)
    _computing_structure_refinement = Column(String)
    _refine_special_details = Column(String)
    _refine_ls_structure_factor_coef = Column(String)
    _refine_ls_weighting_details = Column(String)
    _refine_ls_number_reflns = Column(Integer)
    _refine_ls_number_parameters = Column(Integer)
    _refine_ls_number_restraints = Column(Integer)
    _refine_ls_R_factor_all = Column(MyFloat)
    _refine_ls_R_factor_gt = Column(MyFloat)
    _refine_ls_wR_factor_ref = Column(MyFloat)
    _refine_ls_wR_factor_gt = Column(MyFloat)
    _refine_ls_goodness_of_fit_ref = Column(MyFloat)
    _refine_ls_restrained_S_all = Column(MyFloat)
    _refine_ls_shift_su_max = Column(MyFloat)
    _refine_ls_shift_su_mean = Column(MyFloat)
    _refine_diff_density_max = Column(MyFloat)
    _refine_diff_density_min = Column(MyFloat)
    _diffrn_reflns_av_unetI_netI = Column(MyFloat)
    _database_code_depnum_ccdc_archive = Column(String)
    _shelx_res_file = Column(String)
    modification_time = Column(Date)
    file_size = Column(Integer)


class Cell(Base):
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
    __tablename__ = 'cell'

    Id = Column(Integer, primary_key=True)
    StructureId = Column(Integer, ForeignKey(Structure.Id))
    a = Column(Float)
    b = Column(Float)
    c = Column(Float)
    alpha = Column(Float)
    beta = Column(Float)
    gamma = Column(Float)
    esda = Column(Float)
    esdb = Column(Float)
    esdc = Column(Float)
    esdalpha = Column(Float)
    esdbeta = Column(Float)
    esdgamma = Column(Float)
    volume = Column(Float)

    def values(self):
        return [self.a, self.b, self.c, self.alpha, self.beta, self.gamma, self.volume]

'''
class textsearch(Base):
    """
    textsearch virtual table
    """
    __tablename__ = 'textsearch'

    StructureId = Column(Integer)
    filename = Column(String)
    dataname = Column(String)
    path = Column(String)
    shelx_res_file = Column(String)


class ElementSearch(Base):
    __tablename__ = 'ElementSearch'

    StructureId = Column(Integer)
    _chemical_formula_sum = Column(String)
'''


def init_textsearch(engine: 'Engine'):
    """
    Initializes the full text search (fts) tables.
    """
    with engine.connect() as con:
        con.execute("DROP TABLE IF EXISTS textsearch")
        con.execute("DROP TABLE IF EXISTS ElementSearch")

        # The simple tokenizer is best for my purposes (A self-written tokenizer would even be better):
        con.execute("""
            CREATE VIRTUAL TABLE textsearch USING 
                    fts4(StructureId    INTEGER, 
                         filename       TEXT, 
                         dataname       TEXT, 
                         path           TEXT,
                         shelx_res_file TEXT,
                            tokenize=simple "tokenchars= .=-_");  
                          """
                         )

        # Now the table for element search:
        con.execute("""
            CREATE VIRTUAL TABLE ElementSearch USING
                    fts4(StructureId        INTEGER,
                    _chemical_formula_sum   TEXT,
                        tokenize=simple 'tokenchars= 0123456789');
                      """
                         )

def populate_fulltext_search_table(engine: 'Engine'):
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
    optimize_queries = """INSERT INTO textsearch(txtsearch) VALUES('optimize'); """
    element_search = """
        INSERT INTO ElementSearch(StructureId,
                                _chemical_formula_sum) 
              SELECT Id, _chemical_formula_sum FROM residuals; """
    with engine.connect() as con:
        con.execute(populate_index)
        con.execute(optimize_queries)
        con.execute(element_search)


def get_cell_by_id(session: 'Session', structure_id: str):
    """
    returns the cell of a res file in the db
    """
    if not structure_id:
        return False
    cell = session.query(Cell).filter(Cell.StructureId == structure_id).first()
    if cell.values() and len(cell.values()) > 0:
        return cell.values()
    else:
        return False

def get_symmcards(session: 'Session', structure_id: str):
    """
    Retruns the symm cards of a structure as string list.
    [['x', 'y', 'z'], ['-x', 'y', '-z+1/2'], ... ]
    """
    if not structure_id:
        return False
    symm = session.query(Residuals).filter(Residuals.StructureId == structure_id).first()
    return [x.split(',') for x in symm._space_group_symop_operation_xyz.replace("'", "").replace(" ", "").split("\n")]


def get_atoms_table(session, structure_id, cell, cartesian=False):
    """
    Get atoms in fractional or cartesian coordinates.
    """
    # make sure part is an integer number:
    result = session.query(Atoms).filter(Atoms.StructureId == structure_id)\
                                .filter(Atoms.Name != None).all()
    result = [[at.Name, at.element, at.x, at.y, at.z, at.part, at.occupancy] for at in result]
    if cartesian:
        cartesian_coords = []
        a = lattice.A(cell).orthogonal_matrix
        for at in result:
            cartesian_coords.append(list(at[:2]) + (Array([at[2], at[3], at[4]]) * a).values + list(at[5:]))
        return cartesian_coords
    else:
        return result


def get_residuals(session, structure_id):
    """
    Returns the residuals table values.
    """
    row = session.query(Residuals).filter(Residuals.StructureId == structure_id).first()
    try:
        dic = as_dict(row)
    except AttributeError:
        return False
    return dic


def find_cell_by_volume(session: 'Session', volume: float, threshold: float):
    """
    Searches cells with volume between upper and lower limit
    """
    upper_limit = float(volume + volume * threshold)
    lower_limit = float(volume - volume * threshold)
    volumes = [StructureId for StructureId, in session.query(Cell.StructureId).filter(Cell.volume >= lower_limit)\
                                                .filter(Cell.volume <= upper_limit).all()]
    return volumes

def get_cells_as_list(session: 'Session', structure_ids: list):
    """
    Returns a list of unit cells from the input ids.
    """
    #req = 'select * from cell where StructureId IN ({seq})'.format(seq=self.joined_arglist(structure_ids))
    cells = session.query(Cell).filter(Cell.StructureId.in_(structure_ids)).all()
    result = [[c.a, c.b, c.c, c.alpha, c.beta, c.gamma, c.volume] for c in cells]
    return result

def get_all_structure_names(session, idlist: list = None):
    if idlist:
        # certain ids:
        return session.query(Structure).filter(Structure.Id.in_(idlist)).all()
    else:
        #just all:
        return session.query(Structure).all()


def find_by_date(session, start='0000-01-01', end='NOW'):
    """
    Find structures between start and end date.

    >>> db = StructureTable('../structuredb.sqlite')
    >>> db.database.initialize_db()
    >>> db.find_by_date()
    """
    req = """
          SELECT StructureId FROM Residuals WHERE modification_time between DATE(?) AND DATE(?);
          """
    ids = [StructureId for StructureId, in session.query(Residuals.StructureId)
                        .filter(Residuals.modification_time.between(start, end))]
    return ids


def find_by_strings(engine: 'Engine', text: str):
    """
    Searches for text in the virtual textsearch table.
    """
    ids = []
    req = '''
            SELECT StructureId, filename, dataname, path FROM txtsearch WHERE filename MATCH ?
              UNION
            SELECT StructureId, filename, dataname, path FROM txtsearch WHERE dataname MATCH ?
              UNION
            SELECT StructureId, filename, dataname, path FROM txtsearch WHERE path MATCH ?
              UNION
            SELECT StructureId, filename, dataname, path FROM txtsearch WHERE shelx_res_file MATCH ?
           '''
    with engine.connect() as con:
        try:
            ids = con.execute(req, (text, text, text, text)).fetchall()
        except (TypeError, sqlite3.ProgrammingError, sqlite3.OperationalError) as e:
            print('DB request error in find_by_strings().', e)
            return tuple([])
    return ids


def find_by_it_number(session, number: int) -> list:
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
    result = [sid for sid, in session.query(Residuals.StructureId)
                .filter(Residuals._space_group_IT_number.is_(value)).all()]
    return result


def find_by_elements(session: 'Session', elements: list, anyresult: bool = False) -> list:
    """
    Find structures where certain elements are included in the sum formula.
    TODO: Have to make an element table during index to have a real formula search like in the CSD!
    """
    import re
    matches = []
    # Get all formulas to prevent false negatives with text search in the db:
    result = session.query(Residuals.StructureId, Residuals._chemical_formula_sum).all()
    if result:
        for el in elements:  # The second search excludes false hits like Ca instead of C
            regex = re.compile(r'[\s|\d]?' + el + '[\d|\s]*|[$]+', re.IGNORECASE)
            res = []
            for num, form in result:
                if regex.search(form):
                    # print(form)
                    res.append(num)
            matches.append(res)
    if matches:
        if anyresult:
            return list(set(misc.flatten(matches)))
        else:
            return list(set(matches[0]).intersection(*matches))
    else:
        return []


def fill_structures_table(session, path: str, filename: str, structure_id: str, dataname: str):
    """
    Fills a structure into the database.

    """
    entry = Structure(filename=filename.encode(db_enoding, "ignore"),
                      path=path.encode(db_enoding, "ignore"),
                      dataname=dataname.encode(db_enoding, "ignore"),
                      measurement=structure_id,
                      Id=structure_id)
    a = session.add(entry)
    return a


def fill_cell_table(session: 'Session', structure_id: str, a: float, b: float, c: float,
                    alpha: float, beta: float, gamma:float, volume: float):
    """
    fill the cell of structure(structureId) in the table
    cell = [a, b, c, alpha, beta, gamma]
    """
    aerror = get_error_from_value(a)
    berror = get_error_from_value(b)
    cerror = get_error_from_value(c)
    alphaerror = get_error_from_value(alpha)
    betaerror = get_error_from_value(beta)
    gammaerror = get_error_from_value(gamma)
    vol = volume
    if isinstance(a, str):
        a = a.split('(')[0]
        b = b.split('(')[0]
        c = c.split('(')[0]
        alpha = alpha.split('(')[0]
        beta = beta.split('(')[0]
        gamma = gamma.split('(')[0]
    if isinstance(volume, str):
        vol = volume.split('(')[0]
    entry = Cell(StructureId=structure_id, a=a, b=b, c=c, alpha=alpha, beta=beta, gamma=gamma,
                                      esda=aerror, esdb=berror, esdc=cerror, esdalpha=alphaerror,
                                      esdbeta=betaerror, esdgamma=gammaerror, volume=vol)
    a = session.add(entry)
    return a


def fill_atoms_table(session, structure_id: str, name: str, element: str, x: float, y: float, z: float,
                            occ: float, part: int):
    """
    fill the atoms into structure(structureId)
    """
    atom = Atoms(StructureId=structure_id, Name=name, element=element, x=x, y=y, z=z, occupancy=occ, part=part)
    a = session.add(atom)
    return a


def fill_residuals_table(session: 'Session', structure_id: str, cif: Cif) -> bool:
    """
    Fill the table with residuals of the refinement.
    """
    resid = Residuals(
        StructureId                           = structure_id,
        _cell_formula_units_Z                 = cif.cif_data['_cell_formula_units_Z'],  # Z
        _space_group_name_H_M_alt             = cif.cif_data['_space_group_name_H-M_alt'],  # Raumgruppe (Herman-Maugin)
        _space_group_name_Hall                = cif.cif_data['_space_group_name_Hall'],  # Hall-Symbol
        _space_group_IT_number                = cif.cif_data['_space_group_IT_number'],  # Raumgruppen-Nummer aus IT
        _space_group_crystal_system           = cif.cif_data['_space_group_crystal_system'],  # Kristallsystem
        _space_group_symop_operation_xyz      = cif.cif_data['_space_group_symop_operation_xyz'],  # SYMM cards
        _chemical_formula_sum                 = cif.cif_data['_chemical_formula_sum'],  # Summenformel
        _chemical_formula_weight              = cif.cif_data['_chemical_formula_weight'],  # Moyety-Formel
        _exptl_crystal_description            = cif.cif_data['_exptl_crystal_description'],  # Habitus
        _exptl_crystal_colour                 = cif.cif_data['_exptl_crystal_colour'],  # Farbe
        _exptl_crystal_size_max               = cif.cif_data['_exptl_crystal_size_max'],  # Größe
        _exptl_crystal_size_mid               = cif.cif_data['_exptl_crystal_size_mid'],  # Größe
        _exptl_crystal_size_min               = cif.cif_data['_exptl_crystal_size_min'],  # Größe
        _audit_creation_method                = cif.cif_data['_audit_creation_method'],  # how data were entered into the data block.
        _exptl_absorpt_coefficient_mu         = cif.cif_data['_exptl_absorpt_coefficient_mu'],  # Linear absorption coefficient (mm-1)
        _exptl_absorpt_correction_type        = cif.cif_data['_exptl_absorpt_correction_type'],  # Code for absorption correction
        _diffrn_ambient_temperature           = cif.cif_data['_diffrn_ambient_temperature'],  # The mean temperature in kelvins at which the
        _diffrn_radiation_wavelength          = cif.cif_data['_diffrn_radiation_wavelength'],  # Radiation wavelength (Å)
        _diffrn_radiation_type                = cif.cif_data['_diffrn_radiation_type'],  # Radiation type (e.g. neutron or `Mo Kα')
        _diffrn_source                        = cif.cif_data['_diffrn_source'],  # Röntgenquelle
        _diffrn_measurement_device_type       = cif.cif_data['_diffrn_measurement_device_type'],  # Diffractometer make and type
        _diffrn_reflns_number                 = cif.cif_data['_diffrn_reflns_number'],  # Total number of reflections measured excluding systematic absences
        _diffrn_reflns_av_R_equivalents       = cif.cif_data['_diffrn_reflns_av_R_equivalents'],  # R(int) -> R factor for symmetry-equivalent intensities
        _diffrn_reflns_theta_min              = cif.cif_data['_diffrn_reflns_theta_min'],  # Minimum θ of measured reflections (°)
        _diffrn_reflns_theta_max              = cif.cif_data['_diffrn_reflns_theta_max'],  # Maximum θ of measured reflections (°)
        _diffrn_reflns_theta_full             = cif.cif_data['_diffrn_reflns_theta_full'], # θ to which available reflections are close to 100% complete (°)
        _diffrn_measured_fraction_theta_max   = cif.cif_data['_diffrn_measured_fraction_theta_max'], # completeness, Fraction of unique reflections measured to θmax
        _diffrn_measured_fraction_theta_full  = cif.cif_data['_diffrn_measured_fraction_theta_full'],  # Fraction of unique reflections measured to θfull
        _reflns_number_total                  = cif.cif_data['_reflns_number_total'],  # Number of symmetry-independent reflections excluding systematic absences.
        _reflns_number_gt                     = cif.cif_data['_reflns_number_gt'],  # Number of reflections > σ threshold
        _reflns_threshold_expression          = cif.cif_data['_reflns_threshold_expression'],  # σ expression for F, F2 or I threshold
        _reflns_Friedel_coverage              = cif.cif_data['_reflns_Friedel_coverage'],  # The proportion of Friedel-related reflections present in the number of reported unique reflections
        _computing_structure_solution         = cif.cif_data['_computing_structure_solution'],  # Reference to structure-solution software
        _computing_structure_refinement       = cif.cif_data['_computing_structure_refinement'],  # Reference to structure-refinement software
        _refine_special_details               = cif.cif_data['_refine_special_details'],  # Details about the refinement
        _refine_ls_structure_factor_coef      = cif.cif_data['_refine_ls_structure_factor_coef'],  # Code for F, F2 or I used in least-squares refinement
        _refine_ls_weighting_details          = cif.cif_data['_refine_ls_weighting_details'],  # Weighting expression
        _refine_ls_number_reflns              = cif.cif_data['_refine_ls_number_reflns'],  # The number of unique reflections contributing to the least-squares refinement calculation.
        _refine_ls_number_parameters          = cif.cif_data['_refine_ls_number_parameters'],  # Number of parameters refined
        _refine_ls_number_restraints          = cif.cif_data['_refine_ls_number_restraints'],  # Number of restraints applied during refinement
        _refine_ls_R_factor_all               = cif.cif_data['_refine_ls_R_factor_all'],
        _refine_ls_R_factor_gt                = cif.cif_data['_refine_ls_R_factor_gt'],  # R1 factor of F for reflections > threshold
        _refine_ls_wR_factor_ref              = cif.cif_data['_refine_ls_wR_factor_ref'],  # wR2 factor of coefficient for refinement reflections
        _refine_ls_wR_factor_gt               = cif.cif_data['_refine_ls_wR_factor_gt'],
        _refine_ls_goodness_of_fit_ref        = cif.cif_data['_refine_ls_goodness_of_fit_ref'],  # Goodness of fit S for refinement reflections
        _refine_ls_restrained_S_all           = cif.cif_data['_refine_ls_restrained_S_all'],  # The least-squares goodness-of-fit parameter S' for all reflections after the final cycle of least-squares refinement.
        _refine_ls_shift_su_max               = cif.cif_data['_refine_ls_shift/su_max'],  # Maximum shift/s.u. ratio after final refinement cycle
        _refine_ls_shift_su_mean              = cif.cif_data['_refine_ls_shift/su_mean'],
        _refine_diff_density_max              = cif.cif_data['_refine_diff_density_max'],  # Maximum difference density after refinement
        _refine_diff_density_min              = cif.cif_data['_refine_diff_density_min'],  # Deepest hole
        _diffrn_reflns_av_unetI_netI          = cif.cif_data['_diffrn_reflns_av_unetI/netI'],  # R(sigma)
        _database_code_depnum_ccdc_archive    = cif.cif_data['_database_code_depnum_ccdc_archive'],  # CCDC number
        _shelx_res_file                       = cif.cif_data['_shelx_res_file'],  # The content of the SHELXL res file
        modification_time                     = date(*[int(x) for x in cif.cif_data['modification_time'].split('-')]),
        file_size                             = cif.cif_data['file_size'] )
    a = session.add(resid)
    return a


if __name__ == '__main__':
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine('sqlite:///./test.sqlite')
    Session = sessionmaker(bind=engine)
    session = Session()
    cell = get_cell_by_id(session, 4)
    #print(cell.values())
    #symm = get_symmcards(session, 4)
    #print(symm)
    #atoms = get_atoms_table(session, 4, cell, cartesian=True)
    #print(atoms)
    #ids = find_cell_by_volume(session, 1319, 2)
    #cells = get_cells_as_list(session, ids)
    #print(ids)
    #print(cells)
    string = find_by_strings(engine, '2004805')
    print(string)