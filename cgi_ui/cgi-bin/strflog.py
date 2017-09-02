#!/usr/local/bin/python3.6
#!C:\tools\Python-3.6.2_64\pythonw.exe

import cgi
import pathlib
from string import Template

import sys

import math

import displaymol
from displaymol import mol_file_writer
from lattice import lattice
from pymatgen.core import mat_lattice
from searcher import database_handler
import html
import cgitb

#sys.stderr = sys.stdout
cgitb.enable()

from searcher.database_handler import StructureTable


def application():
    """
    The main application of the StructureFinder web interface.
    <link rel="stylesheet" href="bootstrap3/css/bootstrap.min.css">
    <link rel="stylesheet" href="jasny-bootstrap/css/jasny-bootstrap.min.css">
    <script type="text/javascript" href="jquery/jquery.min.js"></script>
    <script type="text/javascript" href="jasny-bootstrap/js/jasny-bootstrap.min.js"></script>
    """
    ids = []
    print("Content-Type: text/html; charset=utf-8\n")
    form = cgi.FieldStorage()
    cell = form.getvalue("cell")
    text = form.getfirst("text")
    strid = form.getvalue("id")
    mol = form.getvalue("molecule")
    resid1 = form.getvalue("residuals1")
    resid2 = form.getvalue("residuals2")
    dbfilename = "./structuredb.sqlite"
    #dbfilename = "./structures_22.08.2017.sqlite"
    structures = database_handler.StructureTable(dbfilename)
    cif_dic = None
    if strid and (resid1 or resid2):
        request = """select * from residuals where StructureId = {}""".format(strid)
        cif_dic = structures.get_row_as_dict(request)
    if cell:
        ids = find_cell(structures, cell)
        html_txt = process_data(structures, ids).decode('utf-8', 'ignore')
    elif text:
        ids = search_text(structures, text)
        html_txt = process_data(structures, ids).decode('utf-8', 'ignore')
    elif strid and mol:
        cell = structures.get_cell_by_id(strid)[:6]
        m = mol_file_writer.MolFile(strid, structures, cell)
        print(m.make_mol())
        return
    elif strid and resid1:
        print(get_residuals_table1(structures, strid, cif_dic))
        return
    elif strid and resid2:
        print(get_residuals_table2(structures, strid, cif_dic))
        return
    elif strid:
        print(get_all_cif_val_table(structures, strid))
        return
    else:
        html_txt = process_data(structures, ids).decode('utf-8', 'ignore')
    print(html_txt)
    # print(ids)  # For debug
    # print("<br>Cell:", cell)  # For debug


def get_residuals_table1(structures: StructureTable, structure_id: int, cif_dic: dict) -> str:
    """
    Returns a table with the most important residuals of a structure.
    """
    #cell = structures.get_cell_by_id(structure_id)
    if not cif_dic:
        return ""
    table1 = """
    <table class="table table-bordered" id='resitable1'>
        <tbody>
        <tr><td><b>Space Group</b></td>                 <td>{0}</td></tr>
        <tr><td><b>Z</b></td>                           <td>{1}</td></tr>
        <tr><td><b>Sum Formula</b></td>                 <td>{2}</td></tr>
        <tr><td><b>Temperature [K]</b></td>             <td>{3}</td></tr>
        <tr><td><b><i>wR</i><sub>2</sub></b></td>       <td>{4}</td></tr>
        <tr><td><b><i>R<i/><sub>1</sub></b></td>        <td>{5}</td></tr>
        <tr><td><b>Goof</b></td>                        <td>{6}</td></tr>
        <tr><td><b>Max Shift/esd</b></td>               <td>{7}</td></tr>
        <tr><td><b>Peak / Hole [e&angst;<sup>-3</sup>]</b></td>   <td>{8} / {9}</td></tr>
        <tr><td><b><i>R</i>(int)</b></td>               <td>{10}</td></tr>
        <tr><td><b><i>R</i>&sigma;</b></td>             <td>{11}</td></tr>
        </tbody>
    </table>
    """.format(cif_dic['_space_group_name_H_M_alt'],
               cif_dic['_cell_formula_units_Z'],
               cif_dic['_chemical_formula_sum'],
               cif_dic['_diffrn_ambient_temperature'],
               cif_dic['_refine_ls_wR_factor_ref'],
               cif_dic['_refine_ls_R_factor_gt'],
               cif_dic['_refine_ls_goodness_of_fit_ref'],
               cif_dic['_refine_ls_shift_su_max'],
               cif_dic['_refine_diff_density_max'], cif_dic['_refine_diff_density_min'],
               cif_dic['_diffrn_reflns_av_R_equivalents'],
               cif_dic['_diffrn_reflns_av_unetI_netI']
               )
    return table1


def get_residuals_table2(structures: StructureTable, structure_id: int, cif_dic: dict) -> str:
    """
    Returns a table with the most important residuals of a structure.
    """
    #cell = structures.get_cell_by_id(structure_id)
    if not cif_dic:
        return ""
    wavelen = cif_dic['_diffrn_radiation_wavelength']
    thetamax = cif_dic['_diffrn_reflns_theta_max']
    # d = lambda/2sin(theta):
    try:
        d = wavelen / (2 * math.sin(math.radians(thetamax)))
    except(ZeroDivisionError, TypeError):
        d = 0.0
    try:
        compl = cif_dic['_diffrn_measured_fraction_theta_max'] * 100
        if not compl:
            compl = 0.0
    except TypeError:
        compl = 0.0
    table2 = """
    <table class="table table-bordered" id='resitable2'>
        <tbody>
        <tr><td><b>Total num. Refl.</b></td>                 <td>{0}</td></tr>
        <tr><td><b>Parameters</b></td>                           <td>{1}</td></tr>
        <tr><td><b>data/param</b></td>                 <td>{2:<5.1f}</td></tr>
        <tr><td><b>Restraints</b></td>             <td>{3}</td></tr>
        <tr><td><b>&theta;(max) [&deg;]</b></td>       <td>{4}</td></tr>
        <tr><td><b>&theta;(full) [&deg;]</b></td>        <td>{5}</td></tr>
        <tr><td><b>d [&angst;]</b></td>                        <td>{6:5.3f}</td></tr>
        <tr><td><b>complete [%]</b></td>               <td>{7:<5.1f}</td></tr>
        <tr><td><b>Wavelength [&angst;]</b></td>   <td>{8}</td></tr>
        <tr><td><b>CCDC Number</b></td>               <td>{9}</td></tr>
        </tbody>
    </table>
    """.format(cif_dic['_diffrn_reflns_number'],
               cif_dic['_refine_ls_number_parameters'],
               cif_dic['_refine_ls_number_reflns'] / cif_dic['_refine_ls_number_parameters'],
               cif_dic['_refine_ls_number_restraints'],
               thetamax,
               cif_dic['_diffrn_reflns_theta_full'],
               d,
               compl,
               wavelen,
               cif_dic['_database_code_depnum_ccdc_archive']
               )
    return table2


def get_all_cif_val_table(structures: StructureTable, structure_id: int) -> str:
    """
    Returns a html table with the residuals values of a structure.
    """
    # starting table header (the div is for css):
    table_string = """<h4>All CIF values</h4>
                        <div id="myresidualtable">
                        <table class="table table-striped table-bordered" style="white-space: pre">
                            <thead>
                                <tr>
                                    <th> Item </th>
                                    <th> Value </th>
                                </tr>
                            </thead>
                        <tbody>"""
    # get the residuals of the cif file as a dictionary:
    request = """select * from residuals where StructureId = {}""".format(structure_id)
    dic = structures.get_row_as_dict(request)
    if not dic:
        return ""
    # filling table with data rows:
    for key, value in dic.items():
        if key == "Id" or key == "StructureId":
            continue
        if isinstance(value, str):
            value = ''.join([x.replace("\n", "<br>").rstrip('\r\n') for x in value])
        table_string += '''<tr> 
                                <td class="residual-{}"> {} </a></td> 
                                <td> {} </a></td> 
                           </tr> \n'''.format(structure_id, key, value)
    # closing table:
    table_string += """ </tbody>
                        </table>
                        </div>"""
    return table_string


def find_cell(structures: StructureTable, cellstr: str) -> list:
    """
    Finds unit cells in db. Rsturns hits a a list of ids.
    """
    try:
        cell = [float(x) for x in cellstr.strip().split()]
    except (TypeError, ValueError) as e:
        print(e)
        return []
    if len(cell) != 6:
        print("No valid cell!")
        return []
    # if self.ui.moreResultsCheckBox.isChecked() or \
    #        self.ui.ad_moreResultscheckBox.isChecked():
    threshold = 0.08
    ltol = 0.09
    atol = 1.8
    # else:
    #    threshold = 0.03
    #    ltol = 0.001
    #    atol = 1
    # try:
    volume = lattice.vol_unitcell(*cell)
    idlist = structures.find_by_volume(volume, threshold)
    idlist2 = []
    if idlist:
        lattice1 = mat_lattice.Lattice.from_parameters_niggli_reduced(*cell)
        for num, i in enumerate(idlist):
            request = """select * from cell where StructureId = {}""".format(i)
            dic = structures.get_row_as_dict(request)
            try:
                lattice2 = mat_lattice.Lattice.from_parameters(
                    float(dic['a']),
                    float(dic['b']),
                    float(dic['c']),
                    float(dic['alpha']),
                    float(dic['beta']),
                    float(dic['gamma']))
            except ValueError:
                continue
            map = lattice1.find_mapping(lattice2, ltol, atol, skip_rotation_matrix=True)
            if map:
                idlist2.append(i)
    if idlist2:
        return idlist2


def search_text(structures: StructureTable, search_string: str) -> list:
    """
    searches db for given text
    """
    idlist = []
    if len(search_string) == 0:
        return []
    if len(search_string) >= 2:
        if "*" not in search_string:
            search_string = "{}{}{}".format('*', search_string, '*')
    try:
        #  bad hack, should make this return ids like cell search
        idlist = [x[0] for x in structures.find_by_strings(search_string)]
    except AttributeError as e:
        print("Error 1")
        print(e)
    return idlist


def process_data(structures: StructureTable, idlist: list = None):
    """
    Structure.Id,           0
    Structure.measurement,  1
    Structure.path,         2
    Structure.filename,     3
    Structure.dataname      4
    <a href="?id={3}">
    """
    if not structures:
        return []
    table_string = ""
    for i in structures.get_all_structure_names(idlist):
        table_string += '<tr> ' \
                        '   <td> <a id="{3}">{0} </a></td> ' \
                        '   <td> {1} </a></td> ' \
                        '   <td> {2} </a></td> ' \
                        '</tr> \n' \
            .format(i[3].decode('utf-8', errors='ignore'),
                    i[4].decode('utf-8', errors='ignore'),
                    i[2].decode('utf-8', errors='ignore'),
                    i[0]
                    )
        # i[0] -> id
    try:
        p = pathlib.Path("cgi_ui/strflog_Template.htm")
        t = Template(p.read_bytes().decode('utf-8', 'ignore'))
    except FileNotFoundError:
        p = pathlib.Path("./strflog_Template.htm")
        t = Template(p.read_bytes().decode('utf-8', 'ignore'))
    replacedict = {"logtablecolumns": table_string, "CSearch": "Search", "TSearch": "Search"}
    return str(t.safe_substitute(replacedict)).encode('ascii', 'ignore')


if __name__ == "__main__":
    application()
    """
    try:
        import wsgiref.simple_server

        server = wsgiref.simple_server.make_server('127.0.0.1', 8000, application)
        server.serve_forever()
        print("Webserver running...")
    except KeyboardInterrupt:
        print("Webserver stopped...")
    """
