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
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Date, inspect
from sqlalchemy.ext.declarative import declarative_base

import sqlite3
import sys
from sqlite3 import OperationalError

import searcher
from lattice import lattice
from searcher import misc
from searcher.misc import get_error_from_value
from shelxfile.dsrmath import Array

#db_enoding = 'ISO-8859-15'
db_enoding = 'utf-8'

Base = declarative_base()


from sqlalchemy import inspect

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


def as_dict(row) -> dict:
    """
    Returns the content of a specific table row as dictionary.
    """
    return dict((col, getattr(row, col)) for col in row.__table__.columns.keys())


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
    '''
    __tablename__ = 'measurement'

    Id = Column(Integer, primary_key=True)
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
    measurement = Column(Integer, ForeignKey(Measurement.Id))
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
    x = Column(String)
    y = Column(String)
    z = Column(String)
    occupancy = Column(Float)
    part = Column(Integer)

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
    _exptl_crystal_size_max = Column(Float)
    _exptl_crystal_size_mid = Column(Float)
    _exptl_crystal_size_min = Column(Float)
    _exptl_absorpt_coefficient_mu = Column(Float)
    _exptl_absorpt_correction_type = Column(String)
    _diffrn_ambient_temperature = Column(Float)
    _diffrn_radiation_wavelength = Column(Float)
    _diffrn_radiation_type = Column(String)
    _diffrn_source = Column(String)
    _diffrn_measurement_device_type = Column(String)
    _diffrn_reflns_number = Column(Integer)
    _diffrn_reflns_av_R_equivalents = Column(Integer)
    _diffrn_reflns_theta_min = Column(Float)
    _diffrn_reflns_theta_max = Column(Float)
    _diffrn_reflns_theta_full = Column(Float)
    _diffrn_measured_fraction_theta_max = Column(Float)
    _diffrn_measured_fraction_theta_full = Column(Float)
    _reflns_number_total = Column(Integer)
    _reflns_number_gt = Column(Integer)
    _reflns_threshold_expression = Column(String)
    _reflns_Friedel_coverage = Column(Float)
    _computing_structure_solution = Column(String)
    _computing_structure_refinement = Column(String)
    _refine_special_details = Column(String)
    _refine_ls_structure_factor_coef = Column(String)
    _refine_ls_weighting_details = Column(String)
    _refine_ls_number_reflns = Column(Integer)
    _refine_ls_number_parameters = Column(Integer)
    _refine_ls_number_restraints = Column(Integer)
    _refine_ls_R_factor_all = Column(Float)
    _refine_ls_R_factor_gt = Column(Float)
    _refine_ls_wR_factor_ref = Column(Float)
    _refine_ls_wR_factor_gt = Column(Float)
    _refine_ls_goodness_of_fit_ref = Column(Float)
    _refine_ls_restrained_S_all = Column(Float)
    _refine_ls_shift_su_max = Column(Float)
    _refine_ls_shift_su_mean = Column(Float)
    _refine_diff_density_max = Column(Float)
    _refine_diff_density_min = Column(Float)
    _diffrn_reflns_av_unetI_netI = Column(Float)
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


def get_cell_by_id(structure_id: str, session):
    """
    returns the cell of a res file in the db
    """
    if not structure_id:
        return False
    cell = session.query(Cell).filter(Cell.StructureId == structure_id).first()
    if cell and len(cell) > 0:
        return cell
    else:
        return False


if __name__ == '__main__':
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine('sqlite:///./test.sqlite')
    Session = sessionmaker(bind=engine)
    session = Session()
    cell = session.query(Cell).filter(Cell.StructureId == 4).first()
    print(cell.values())