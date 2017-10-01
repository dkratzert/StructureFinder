#!/usr/local/bin/python3.6
# !C:\tools\Python-3.6.2_64\pythonw.exe

import cgi
import pathlib
import json
import math

from displaymol import mol_file_writer
from lattice import lattice
from pymatgen.core import mat_lattice
from searcher import database_handler, misc

from searcher.database_handler import StructureTable
import cgitb

cgitb.enable()

"""
TODO:

"""

# dbfilename = "./structuredb.sqlite"
dbfilename = "./structures_30.09.2017.sqlite"


def application(dbfilename):
    """
    The main application of the StructureFinder web interface.
    """
    ids = []
    print("Content-Type: text/html; charset=utf-8\n")
    form = cgi.FieldStorage()
    cell_search = form.getvalue("cell_search")
    text_search = form.getfirst("text_search")
    more_results = (form.getfirst("more") == "true")
    sublattice = (form.getfirst("supercell") == "true")
    str_id = form.getvalue("id")
    mol = form.getvalue("molecule")
    resid1 = form.getvalue("residuals1")
    resid2 = form.getvalue("residuals2")
    unitcell = form.getvalue("unitcell")
    adv = (form.getfirst("adv") == "true")
    records = form.getfirst('cmd')
    structures = database_handler.StructureTable(dbfilename)
    cif_dic = None
    # debug_output(cell_search, text_search, more_results, sublattice, str_id, mol, resid1, resid2, unitcell, adv)
    if adv:
        elincl = form.getvalue("elements_in")
        elexcl = form.getvalue("elements_out")
        txt_in = form.getvalue("text_in")
        txt_ex = form.getvalue("text_out")
        date1 = form.getvalue("date1")
        date2 = form.getvalue("date2")
        # debug_output(cell_search, text_search, more_results, sublattice, str_id, mol, resid1, resid2,
        # unitcell, adv, date1, date2)
        ids = advanced_search(cellstr=cell_search, elincl=elincl, elexcl=elexcl, txt=txt_in, txt_ex=txt_ex,
                              sublattice=sublattice, more_results=more_results, date1=date1, date2=date2,
                              structures=structures)
        print(get_structures_json(structures, ids))
        return
    if str_id and (resid1 or resid2):
        request = """select * from residuals where StructureId = {}""".format(str_id)
        cif_dic = structures.get_row_as_dict(request)
    if cell_search:
        ids = find_cell(structures, cell_search, more_results=more_results, sublattice=sublattice)
        print(get_structures_json(structures, ids))
        return
    elif text_search:
        ids = search_text(structures, text_search)
        print(get_structures_json(structures, ids))
        return
    elif str_id and mol:
        cell_list = structures.get_cell_by_id(str_id)[:6]
        m = mol_file_writer.MolFile(str_id, structures, cell_list)
        print(m.make_mol())
        return
    elif str_id and unitcell:
        print(get_cell_parameters(structures, str_id))
        return
    elif str_id and resid1:
        print(get_residuals_table1(cif_dic))
        return
    elif str_id and resid2:
        print(get_residuals_table2(cif_dic))
        return
    elif str_id:
        print(get_all_cif_val_table(structures, str_id))
        return
    if records == 'get-records':
        print(get_structures_json(structures))
        return
    else:
        ids = []
        html_txt = process_data()
    print(html_txt)


def debug_output(cell_search, text_search, more_results, sublattice, strid, mol,
                 resid1, resid2, unitcell, adv, date1="", date2=""):
    p = pathlib.Path('test.log')
    p.write_text("cell_search: {} \n"
                 "text_search: {} \n"
                 "more_results: {} \n"
                 "sublattice: {} \n"
                 "strid: {} \n"
                 "mol: {} \n"
                 "resid1: {} \n"
                 "resid2: {} \n"
                 "unitcell: {} \n"
                 "date1: {} \n"
                 "date2: {} \n"
                 "adv: {} \n\n\n\n\n".format(cell_search, text_search, more_results,
                                             sublattice, strid, mol, resid1, resid2, unitcell,
                                             date1, date2, adv
                                             ))


def get_structures_json(structures: StructureTable, ids: list = None) -> dict:
    """
    Returns the next package of table rows for continuos scrolling.
    """
    dic = structures.get_all_structures_as_dict(ids)
    return json.dumps({"total": len(dic), "records": dic, "status": "success"}, indent=2)


def get_cell_parameters(structures: StructureTable, strid: str) -> str:
    """
    Resturns unit cell parameters as html formated string.
    """
    c = structures.get_cell_by_id(strid)
    cstr = """<b>Unit Cell:</b>&nbsp;&nbsp; 
                      <i>a</i> = {0:>8.3f}&nbsp;&angst;,&nbsp;
                      <i>b</i> = {1:>8.3f}&nbsp;&angst;,&nbsp;
                      <i>c</i> = {2:>8.3f}&nbsp;&angst;,&nbsp; 
                      <i>&alpha;</i> = {3:>8.3f}&deg;,&nbsp;
                      <i>&beta;</i> = {4:>8.3f}&deg;,&nbsp;
                      <i>&gamma;</i> = {5:>8.3f}&deg;,&nbsp;
                      <i>V</i> = {6}&nbsp;&angst;<sup>3</sup>&nbsp;&nbsp;&nbsp;&nbsp; 
            <div class='hidden' id='hidden-cell'>{0}  {1}  {2}  {3}  {4}  {5}</div>          
            
            """.format(*c)
    return cstr


def get_residuals_table1(cif_dic: dict) -> str:
    """
    Returns a table with the most important residuals of a structure.
    """
    if cif_dic['_diffrn_reflns_av_unetI_netI']:
        rsigma = " / {}".format(cif_dic['_diffrn_reflns_av_unetI_netI'])
    else:
        rsigma = " "
    if not cif_dic:
        return ""
    if cif_dic['_refine_diff_density_max']:
        peakhole = "{} / {}".format(cif_dic['_refine_diff_density_max'], cif_dic['_refine_diff_density_min'])
    else:
        peakhole = " "
    table1 = """
    <table class="table table-bordered" id='resitable1'>
        <tbody>
        <tr><td style='width: 40%'><b>Space Group</b></td>                 <td>{0}</td></tr>
        <tr><td><b>Z</b></td>                           <td>{1}</td></tr>
        <tr><td><b>Sum Formula</b></td>                 <td>{2}</td></tr>
        <tr><td><b>Temperature [K]</b></td>             <td>{3}</td></tr>
        <tr><td><b><i>wR</i><sub>2</sub></b></td>       <td>{4}</td></tr>
        <tr><td><b><i>R<i/><sub>1</sub></b></td>        <td>{5}</td></tr>
        <tr><td><b>Goof</b></td>                        <td>{6}</td></tr>
        <tr><td><b>Max Shift/esd</b></td>               <td>{7}</td></tr>
        <tr><td><b>Peak / Hole [e&angst;<sup>&minus;3</sup>]</b></td>             <td>{8}</td></tr>
        <tr><td><b><i>R</i><sub>int</sub> / <i>R</i>&sigma;</b></b></td>    <td>{9}{10} </td></tr>
        <tr><td><b>Wavelength [&angst;]</b></td>                      <td>{11}</td></tr>
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
               peakhole,
               cif_dic['_diffrn_reflns_av_R_equivalents'],
               rsigma,
               cif_dic['_diffrn_radiation_wavelength']
               )
    return table1


def get_residuals_table2(cif_dic: dict) -> str:
    """
    Returns a table with the most important residuals of a structure.
    """
    # cell = structures.get_cell_by_id(structure_id)
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
    try:
        data_to_param = cif_dic['_refine_ls_number_reflns'] / cif_dic['_refine_ls_number_parameters']
    except TypeError:
        data_to_param = 0
    table2 = """
    <table class="table table-bordered" id='resitable2'>
        <tbody>
        <tr><td style='width: 40%'><b>Measured Refl.</b></td>       <td>{0}</td></tr>
        <tr><td><b>Independent Refl.</b></td>                       <td>{9}</td></tr>
        <tr><td><b>Indep. Refl. [<i>I</i>>2&sigma;(<i>I</i>)] </b></td>                       <td>{10}</td></tr>
        <tr><td><b>Parameters</b></td>                              <td>{1}</td></tr>
        <tr><td><b>data/param</b></td>                              <td>{2:<5.1f}</td></tr>
        <tr><td><b>Restraints</b></td>                              <td>{3}</td></tr>
        <tr><td><b>&theta;<sub>max</sub> [&deg;]</b></td>                    <td>{4}</td></tr>
        <tr><td><b>&theta;<sub>full</sub> [&deg;]</b></td>                   <td>{5}</td></tr>
        <tr><td><b>d [&angst;]</b></td>                             <td>{6:5.3f}</td></tr>
        <tr><td><b>completeness [%]</b></td>                            <td>{7:<5.1f}</td></tr>
        <tr><td><b>CCDC Number</b></td>                             <td>{8}</td></tr>
        </tbody>
    </table>
    """.format(cif_dic['_diffrn_reflns_number'],
               cif_dic['_refine_ls_number_parameters'],
               data_to_param,
               cif_dic['_refine_ls_number_restraints'],
               thetamax,
               cif_dic['_diffrn_reflns_theta_full'],
               d,
               compl,
               cif_dic['_database_code_depnum_ccdc_archive'],
               cif_dic['_refine_ls_number_reflns'],
               cif_dic['_reflns_number_gt']
               )
    return table2


def get_all_cif_val_table(structures: StructureTable, structure_id: int) -> str:
    """
    Returns a html table with the residuals values of a structure.
    """
    # starting table header (the div is for css):
    # style="white-space: pre": preserves white space
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


def find_cell(structures: StructureTable, cellstr: str, sublattice=False, more_results=False) -> list:
    """
    Finds unit cells in db. Rsturns hits a a list of ids.
    """
    try:
        cell = [float(x) for x in cellstr.strip().split()]
    except (TypeError, ValueError) as e:
        # print(e)
        return []
    if len(cell) != 6:
        return []
    if more_results:
        threshold = 0.08
        ltol = 0.09
        atol = 1.8
    else:
        threshold = 0.03
        ltol = 0.001
        atol = 1
    volume = lattice.vol_unitcell(*cell)
    if sublattice:
        vol0 = volume * 0.25
        vol1 = volume * 0.5
        vol2 = volume * 2
        vol3 = volume * 3
        vol4 = volume * 4
        idlist = []
        for v in (volume, vol0, vol1, vol2, vol3, vol4):
            # First a list of structures where the volume is similar:
            idlist.extend(structures.find_by_volume(v, threshold))
    else:
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
        pass
        # print("Error 1")
        # print(e)
    return idlist


def search_elements(structures: StructureTable, elements: str, anyresult: bool = False) -> list:
    """
    list(set(l).intersection(l2))
    """
    formula = []
    res = []
    try:
        formula = misc.get_list_of_elements(elements)
    except KeyError:
        return []
    try:
        res = structures.find_by_elements(formula, anyresult=anyresult)
    except AttributeError:
        pass
    return list(res)


def find_dates(structures: StructureTable, date1: str, date2: str) -> list:
    """
    Returns a list if id between date1 and date2
    """
    if not date1:
        date1 = '0000-01-01'
    if not date2:
        date2 = 'NOW'
    result = structures.find_by_date(date1, date2)
    return result


def advanced_search(cellstr: str, elincl, elexcl, txt, txt_ex, sublattice, more_results,
                    date1: str = None, date2: str = None, structures=None) -> list:
    """
    Combines all the search fields. Collects all includes, all excludes ad calculates
    the difference.
    """
    excl = []
    incl = []
    date_results = []
    results = []
    cell = []
    if cellstr:
        cell = [float(x) for x in cellstr.strip().split()]
    if cell and len(cell) == 6:
        cellres = find_cell(structures, cellstr, sublattice=sublattice, more_results=more_results)
        incl.append(cellres)
    if elincl:
        incl.append(search_elements(structures, elincl))
    if any([date1, date2]):
        date_results = find_dates(structures, date1, date2)
    if txt:
        if len(txt) >= 2 and "*" not in txt:
            txt = '*' + txt + '*'
        idlist = structures.find_by_strings(txt)
        try:
            incl.append([i[0] for i in idlist])
        except(IndexError, KeyError):
            incl.append([idlist])  # only one result
    if elexcl:
        excl.append(search_elements(structures, elexcl, anyresult=True))
    if txt_ex:
        if len(txt_ex) >= 2 and "*" not in txt_ex:
            txt_ex = '*' + txt_ex + '*'
        idlist = structures.find_by_strings(txt_ex)
        try:
            excl.append([i[0] for i in idlist])
        except(IndexError, KeyError):
            excl.append([idlist])  # only one result
    if incl:
        results = set(incl[0]).intersection(*incl)
        if date_results:
            results = set(date_results).intersection(results)
    else:
        results = date_results
    if excl:
        # excl list should not be in the resukts at all
        return list(results - set(misc.flatten(excl)))
    return list(results)


def process_data():
    """
    Reads html template and replaces things.
    """
    try:
        p = pathlib.Path("cgi_ui/strf_web_Template.htm")
        t = p.read_bytes().decode('utf-8', 'ignore')
    except FileNotFoundError:
        p = pathlib.Path("./strf_web_Template.htm")
        t = p.read_bytes().decode('utf-8', 'ignore')
    return t


if __name__ == "__main__":
    application(dbfilename)
