from typing import Any, List

from sqlalchemy import Column, Date, Float, ForeignKey, Index, Integer, String, Text, inspect, alias
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped
from sqlalchemy.types import TypeDecorator, Float


class Base(DeclarativeBase):
    def _asdict(self) -> dict[str, Any]:
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}


metadata = Base.metadata


class FloatType(TypeDecorator):
    impl = Float

    def process_bind_param(self, value: str, dialect):
        """
        Method is called when a value is being written to the database
        """
        try:
            return float(value)
        except ValueError:
            return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return float(value)


class Structure(Base):
    __tablename__ = 'Structure'

    Id = Column(Integer, primary_key=True)
    measurement = Column(ForeignKey('Structure.Id'), nullable=True)
    path = Column(Text)
    filename = Column(Text)
    dataname = Column(Text)

    Structure = relationship('Structure', remote_side=[Id], back_populates='Structure_reverse')
    Structure_reverse = relationship('Structure', remote_side=[measurement], back_populates='Structure')
    Atoms: Mapped[List['Atoms']] = relationship('Atoms')
    Residuals: Mapped['Residuals'] = relationship('Residuals')
    authors: Mapped['Authors'] = relationship('Authors', back_populates='Structure_')
    cell: Mapped['Cell'] = relationship('Cell', back_populates='Structure_', uselist=False)
    sum_formula: Mapped['SumFormula'] = relationship('SumFormula', back_populates='Structure_')


class DatabaseFormat(Base):
    __tablename__ = 'database_format'

    Id = Column(Integer, primary_key=True)
    Format = Column(Integer)


class Measurement(Base):
    __tablename__ = 'measurement'

    Id = Column(Integer, primary_key=True)
    name = Column(String(255))


class Atoms(Base):
    __tablename__ = 'Atoms'
    molindex: int = 0

    Id = Column(Integer, primary_key=True)
    StructureId = Column(ForeignKey('Structure.Id'), nullable=False)
    Name = Column(Text)
    element = Column(Text)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)
    occupancy = Column(Float)
    part = Column(Integer)
    xc = Column(Float)
    yc = Column(Float)
    zc = Column(Float)

    Structure_: Mapped["Structure"] = relationship('Structure', back_populates='Atoms')


class Residuals(Base):
    __tablename__ = 'Residuals'
    __table_args__ = (
        Index('idx_ccd', '_database_code_depnum_ccdc_archive'),
        Index('idx_itnum', '_space_group_IT_number'),
        Index('idx_modiftime', 'modification_time'),
        Index('idx_spgr', '_space_group_IT_number')
    )

    Id = Column(Integer, primary_key=True)
    StructureId = Column(ForeignKey('Structure.Id'), nullable=False)
    _cell_formula_units_Z = Column(Integer)
    _space_group_name_H_M_alt = Column(Text)
    _space_group_name_Hall = Column(Text)
    _space_group_centring_type = Column(Text)
    _space_group_IT_number = Column(Integer)
    _space_group_crystal_system = Column(Text)
    _space_group_symop_operation_xyz: Mapped[str] = Column(Text)
    _audit_creation_method = Column(Text)
    _chemical_formula_sum = Column(Text)
    _chemical_formula_weight = Column(Text)
    _exptl_crystal_description = Column(Text)
    _exptl_crystal_colour = Column(Text)
    _exptl_crystal_size_max = Column(FloatType)
    _exptl_crystal_size_mid = Column(FloatType)
    _exptl_crystal_size_min = Column(FloatType)
    _exptl_absorpt_coefficient_mu = Column(FloatType)
    _exptl_absorpt_correction_type = Column(Text)
    _diffrn_ambient_temperature = Column(FloatType)
    _diffrn_radiation_wavelength = Column(FloatType)
    _diffrn_radiation_type = Column(Text)
    _diffrn_source = Column(Text)
    _diffrn_measurement_device_type = Column(Text)
    _diffrn_reflns_number = Column(Integer)
    _diffrn_reflns_av_R_equivalents = Column(Integer)
    _diffrn_reflns_theta_min = Column(FloatType)
    _diffrn_reflns_theta_max = Column(FloatType)
    _diffrn_reflns_theta_full = Column(FloatType)
    _diffrn_measured_fraction_theta_max = Column(FloatType)
    _diffrn_measured_fraction_theta_full = Column(FloatType)
    _reflns_number_total = Column(Integer)
    _reflns_number_gt = Column(Integer)
    _reflns_threshold_expression = Column(Text)
    _reflns_Friedel_coverage = Column(FloatType)
    _computing_structure_solution = Column(Text)
    _computing_structure_refinement = Column(Text)
    _refine_special_details = Column(Text)
    _refine_ls_abs_structure_Flack = Column(Text)
    _refine_ls_structure_factor_coef = Column(Text)
    _refine_ls_weighting_details = Column(Text)
    _refine_ls_number_reflns = Column(Integer)
    _refine_ls_number_parameters = Column(Integer)
    _refine_ls_number_restraints = Column(Integer)
    _refine_ls_R_factor_all = Column(FloatType)
    _refine_ls_R_factor_gt = Column(FloatType)
    _refine_ls_wR_factor_ref = Column(FloatType)
    _refine_ls_wR_factor_gt = Column(FloatType)
    _refine_ls_goodness_of_fit_ref = Column(FloatType)
    _refine_ls_restrained_S_all = Column(FloatType)
    _refine_ls_shift_su_max = Column(FloatType)
    _refine_ls_shift_su_mean = Column(FloatType)
    _refine_diff_density_max = Column(FloatType)
    _refine_diff_density_min = Column(FloatType)
    _diffrn_reflns_av_unetI_netI = Column(FloatType)
    _database_code_depnum_ccdc_archive = Column(Text)
    _shelx_res_file = Column(Text)
    modification_time = Column(Date)
    file_size = Column(Integer)

    Structure_: Mapped["Structure"] = relationship('Structure', back_populates='Residuals')


class Authors(Base):
    __tablename__ = 'authors'

    Id = Column(Integer, primary_key=True)
    StructureId = Column(ForeignKey('Structure.Id'), nullable=False)
    _audit_author_name = Column(Text)
    _audit_contact_author_name = Column(Text)
    _publ_contact_author_name = Column(Text)
    _publ_contact_author = Column(Text)
    _publ_author_name = Column(Text)

    Structure_ = relationship('Structure', back_populates='authors')


class Cell(Base):
    __tablename__ = 'cell'
    __table_args__ = (
        Index('idx_a', 'a'),
        Index('idx_al', 'alpha'),
        Index('idx_b', 'b'),
        Index('idx_be', 'beta'),
        Index('idx_c', 'c'),
        Index('idx_ga', 'gamma'),
        Index('idx_volume', 'volume')
    )

    Id = Column(Integer, primary_key=True)
    StructureId = Column(ForeignKey('Structure.Id'), nullable=False)
    a = Column(Float)
    b = Column(Float)
    c = Column(Float)
    alpha = Column(Float)
    beta = Column(Float)
    gamma = Column(Float)
    volume = Column(Float)

    Structure_ = relationship('Structure', back_populates='cell')


class SumFormula(Base):
    __tablename__ = 'sum_formula'

    Id = Column(Integer, primary_key=True)
    StructureId = Column(ForeignKey('Structure.Id'), nullable=False)
    Elem_C = Column(Float)
    Elem_D = Column(Float)
    Elem_H = Column(Float)
    Elem_N = Column(Float)
    Elem_O = Column(Float)
    Elem_Cl = Column(Float)
    Elem_Br = Column(Float)
    Elem_I = Column(Float)
    Elem_F = Column(Float)
    Elem_S = Column(Float)
    Elem_P = Column(Float)
    Elem_Ac = Column(Float)
    Elem_Ag = Column(Float)
    Elem_Al = Column(Float)
    Elem_Am = Column(Float)
    Elem_Ar = Column(Float)
    Elem_As = Column(Float)
    Elem_At = Column(Float)
    Elem_Au = Column(Float)
    Elem_B = Column(Float)
    Elem_Ba = Column(Float)
    Elem_Be = Column(Float)
    Elem_Bi = Column(Float)
    Elem_Bk = Column(Float)
    Elem_Ca = Column(Float)
    Elem_Cd = Column(Float)
    Elem_Ce = Column(Float)
    Elem_Cf = Column(Float)
    Elem_Cm = Column(Float)
    Elem_Co = Column(Float)
    Elem_Cr = Column(Float)
    Elem_Cs = Column(Float)
    Elem_Cu = Column(Float)
    Elem_Dy = Column(Float)
    Elem_Er = Column(Float)
    Elem_Eu = Column(Float)
    Elem_Fe = Column(Float)
    Elem_Fr = Column(Float)
    Elem_Ga = Column(Float)
    Elem_Gd = Column(Float)
    Elem_Ge = Column(Float)
    Elem_He = Column(Float)
    Elem_Hf = Column(Float)
    Elem_Hg = Column(Float)
    Elem_Ho = Column(Float)
    Elem_In = Column(Float)
    Elem_Ir = Column(Float)
    Elem_K = Column(Float)
    Elem_Kr = Column(Float)
    Elem_La = Column(Float)
    Elem_Li = Column(Float)
    Elem_Lu = Column(Float)
    Elem_Mg = Column(Float)
    Elem_Mn = Column(Float)
    Elem_Mo = Column(Float)
    Elem_Na = Column(Float)
    Elem_Nb = Column(Float)
    Elem_Nd = Column(Float)
    Elem_Ne = Column(Float)
    Elem_Ni = Column(Float)
    Elem_Np = Column(Float)
    Elem_Os = Column(Float)
    Elem_Pa = Column(Float)
    Elem_Pb = Column(Float)
    Elem_Pd = Column(Float)
    Elem_Pm = Column(Float)
    Elem_Po = Column(Float)
    Elem_Pr = Column(Float)
    Elem_Pt = Column(Float)
    Elem_Pu = Column(Float)
    Elem_Ra = Column(Float)
    Elem_Rb = Column(Float)
    Elem_Re = Column(Float)
    Elem_Rh = Column(Float)
    Elem_Rn = Column(Float)
    Elem_Ru = Column(Float)
    Elem_Sb = Column(Float)
    Elem_Sc = Column(Float)
    Elem_Se = Column(Float)
    Elem_Si = Column(Float)
    Elem_Sm = Column(Float)
    Elem_Sn = Column(Float)
    Elem_Sr = Column(Float)
    Elem_Ta = Column(Float)
    Elem_Tb = Column(Float)
    Elem_Tc = Column(Float)
    Elem_Te = Column(Float)
    Elem_Th = Column(Float)
    Elem_Ti = Column(Float)
    Elem_Tl = Column(Float)
    Elem_Tm = Column(Float)
    Elem_U = Column(Float)
    Elem_V = Column(Float)
    Elem_W = Column(Float)
    Elem_Xe = Column(Float)
    Elem_Y = Column(Float)
    Elem_Yb = Column(Float)
    Elem_Zn = Column(Float)
    Elem_Zr = Column(Float)

    Structure_ = relationship('Structure', back_populates='sum_formula')
