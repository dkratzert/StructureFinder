# -*- coding: utf-8 -*-
# !C:\tools\Python-3.6.2_64\pythonw.exe
# !/usr/local/bin/python3.6

###########################################################
###  Configure the web server here:   #####################

host = "10.6.13.3"
port = "80"
dbfilename = "../structurefinder.sqlite"

###########################################################

import socket

names = ['PC9', 'DDT-2.local']
# run on local ip on my PC:
# print(socket.gethostname())
if socket.gethostname() in names:
    host = '127.0.0.1'
    port = "8080"
    dbfilename = "./test.sqlite"
site_ip = host + ':' + port

import math
import os
import sys
from pathlib import Path
from xml.etree.ElementTree import ParseError

try:  # Adding local path to PATH
    sys.path.insert(0, os.path.abspath('./'))
except(KeyError, ValueError):
    print('Unable to set PATH properly. strf_web.py might not work.')

pyver = sys.version_info
if pyver[0] == 3 and pyver[1] < 4:
    # Python 2 creates a syntax error anyway.
    print("You need Python 3.4 and up in oder to run this proram!")
    sys.exit()

from shutil import which
from searcher.constants import centering_letter_2_num, centering_num_2_letter
from ccdc.query import get_cccsd_path, search_csd, parse_results
from cgi_ui.bottle import Bottle, static_file, template, redirect, request, response
from displaymol.mol_file_writer import MolFile
from displaymol.sdm import SDM
from lattice import lattice
from pymatgen.core import mat_lattice
from searcher.database_handler import StructureTable
from searcher.misc import is_valid_cell, get_list_of_elements, flatten, is_a_nonzero_file, format_sum_formula, \
    combine_results

"""
TODO:
- Make login infrastructure.
- Maybe http://www.daterangepicker.com
"""

app = application = Bottle()


@app.get('/all')
def structures_list_data():
    """
    The content of the structures list.
    """
    structures = StructureTable(dbfilename)
    return get_structures_json(structures, show_all=True)


@app.get('/')
def main():
    """
    The main web site with html template.
    """
    response.set_header('Set-Cookie', 'str_id=')
    response.content_type = 'text/html; charset=UTF-8'
    data = {"my_ip": site_ip,
            "title": 'StructureFinder',
            'host' : host}
    output = template('./cgi_ui/views/strf_web', data)
    return output


@app.get('/dbfile.sqlite')
def get_dbfile():
    return Path(dbfilename).read_bytes()


@app.get("/cellsrch")
def cellsrch():
    cell_search = request.GET.cell_search
    more_results = (request.GET.more == "true")
    sublattice = (request.GET.supercell == "true")
    cell = is_valid_cell(cell_search)
    print("Cell search:", cell)
    structures = StructureTable(dbfilename)
    if cell:
        ids = find_cell(structures, cell, more_results=more_results, sublattice=sublattice)
        print("--> Got {} structures from cell search.".format(len(ids)))
        return get_structures_json(structures, ids)


@app.get("/txtsrch")
def txtsrch():
    structures = StructureTable(dbfilename)
    text_search = request.GET.text_search
    print("Text search:", text_search)
    ids = search_text(structures, text_search)
    return get_structures_json(structures, ids)


@app.get("/adv_srch")
def adv():
    elincl = request.GET.elements_in
    elexcl = request.GET.elements_out
    date1 = request.GET.date1
    date2 = request.GET.date2
    cell_search = request.GET.cell_search
    txt_in = request.GET.text_in
    txt_out = request.GET.text_out
    if len(txt_in) >= 2 and "*" not in txt_in:
        txt_in = '*' + txt_in + '*'
    if len(txt_out) >= 2 and "*" not in txt_out:
        txt_out = '*' + txt_out + '*'
    more_results = (request.GET.more == "true")
    sublattice = (request.GET.supercell == "true")
    onlyelem = (request.GET.onlyelem == "true")
    it_num = request.GET.it_num
    structures = StructureTable(dbfilename)
    print("Advanced search: elin:", elincl, 'elout:', elexcl, date1, '|', date2, '|', cell_search, 'txin:', txt_in,
          'txout:', txt_out, '|', 'more:', more_results, 'Sublatt:', sublattice, 'It-num:', it_num, 'only:', onlyelem)
    ids = advanced_search(cellstr=cell_search, elincl=elincl, elexcl=elexcl, txt=txt_in, txt_ex=txt_out,
                          sublattice=sublattice, more_results=more_results, date1=date1, date2=date2,
                          structures=structures, it_num=it_num, onlythese=onlyelem)
    print("--> Got {} structures from Advanced search.".format(len(ids)))
    return get_structures_json(structures, ids)


@app.post('/molecule')
def jsmol_request():
    """
    A request for atom data from jsmol.
    """
    str_id = request.POST.id
    print("Molecule id:", str_id)
    structures = StructureTable(dbfilename)
    if str_id:
        cell = structures.get_cell_by_id(str_id)
        if request.POST.grow == 'true':
            symmcards = [x.split(',') for x in structures.get_row_as_dict(str_id)
            ['_space_group_symop_operation_xyz'].replace("'", "").replace(" ", "").split("\n")]
            atoms = structures.get_atoms_table(str_id, cell[:6], cartesian=False, as_list=True)
            if atoms:
                sdm = SDM(atoms, symmcards, cell)
                needsymm = sdm.calc_sdm()
                atoms = sdm.packer(sdm, needsymm)
        else:
            atoms = structures.get_atoms_table(str_id, cell[:6], cartesian=True, as_list=False)
        try:
            m = MolFile(atoms)
            return m.make_mol()
        except(KeyError, TypeError) as e:
            print('Exception in jsmol_request: {}'.format(e))
            return ''


@app.post('/residuals')
def post_request():
    """
    Handle POST requests.
    """
    cif_dic = {}
    str_id = request.POST.id
    response.set_header('Set-Cookie', 'str_id=' + str_id)
    resid1 = request.POST.residuals1 == 'true'
    resid2 = request.POST.residuals2 == 'true'
    all_cif = request.POST.all == 'true'
    unitcell = request.POST.unitcell
    structures = StructureTable(dbfilename)
    print("Structure id:", str_id)
    if str_id:
        cif_dic = structures.get_row_as_dict(str_id)
    if str_id and unitcell and not (resid1 or resid2 or all_cif):
        try:
            return get_cell_parameters(structures, str_id)
        except ValueError as e:
            print("Exception raised:")
            print(e)
            return ''
    if str_id and resid1:
        return get_residuals_table1(structures, cif_dic, str_id)
    if str_id and resid2:
        return get_residuals_table2(cif_dic)
    if str_id and all_cif:
        return get_all_cif_val_table(structures, str_id)


@app.route('/static/<filepath:path>')
def server_static(filepath):
    """
    Static files such as images or CSS files are not served automatically.
    The static_file() function is a helper to serve files in a safe and convenient way (see Static Files).
    This example is limited to files directly within the /path/to/your/static/files directory because the
    <filename> wildcard won’t match a path with a slash in it. To serve files in subdirectories, change
    the wildcard to use the path filter:
    """
    response = static_file(filepath, root='./cgi_ui/static/')
    response.set_header("Cache-Control", "public, max-age=240")
    return response


@app.route('/version')
def version():
    from misc.version import VERSION
    return 'version ' + str(VERSION)


@app.get('/cellcheck')
def cellsearch():
    if sys.platform == 'win32':
        if not get_cccsd_path():
            return 'false'
        else:
            return 'true'
    else:
        try:
            if which('ccdc_searcher') or \
                    Path('/opt/CCDC/CellCheckCSD/bin/ccdc_searcher').exists():
                print('CellCheckCSD found')
                return 'true'
        except TypeError:
            return 'false'


@app.route('/favicon.ico')
def redirect_to_favicon():
    redirect('/static/favicon.ico')


@app.get('/csd')
def show_cellcheck():
    """
    Shows the CellcheckCSD web page
    """
    structures = StructureTable(dbfilename)
    str_id = request.get_cookie('str_id')
    centering = ''
    if str_id:
        cell = structures.get_cell_by_id(str_id)
        cif_dic = structures.get_row_as_dict(str_id)
        try:
            centering = cif_dic['_space_group_centring_type']
        except KeyError:
            centering = ''
        # formula = structures.get_calc_sum_formula(str_id)
        # print(formula)
        cellstr = '{:>8.3f} {:>8.3f} {:>8.3f} {:>8.3f} {:>8.3f} {:>8.3f}'.format(*cell)
    else:
        cellstr = ''
        # formula = ''
    if centering:
        try:
            cent = centering_letter_2_num[centering]
        except KeyError:  # mostly value of '?'
            cent = 0
    else:
        cent = 0
    response.content_type = 'text/html; charset=UTF-8'
    data = {"my_ip" : site_ip,
            "title" : 'StructureFinder',
            'str_id': cellstr, 'cent': cent,
            'host'  : host}
    output = template('./cgi_ui/views/cellcheckcsd', data)
    # 'formula': formula_dict_to_elements(formula)}
    return output


@app.post('/csd-list')
def search_cellcheck_csd():
    """
    Search with CellcheckCSD.
    """
    cmd = request.POST.cmd
    cell = request.POST.cell
    if not cell:
        return {}
    cent = request.POST.centering
    if len(cell) < 6:
        return {}
    if cmd == 'get-records' and len(cell.split()) == 6:
        xml = search_csd(cell.split(), centering=centering_num_2_letter[int(cent)])
        # print(xml)
        try:
            results = parse_results(xml)  # results in a dictionary
        except ParseError as e:
            print(e)
            return
        # print(results)
        print(len(results), 'Structures found...')
        return {"total": len(results), "records": results, "status": "success"}
    else:
        return {}


@app.error(404)
def error404(error):
    """
    Redefine 404 message.
    """
    return '''<div style="text-align: center;">
                <b>Nothing here, sorry.</b><br>
                <p>
                <a href="http://{}{}/">Back to main page</a>
                </p>
              </div>
            '''.format(host, ':' + port)


def is_ajax():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return True
    else:
        return False


def get_structures_json(structures: StructureTable, ids: (list, tuple) = None, show_all: bool = False) -> dict:
    """
    Returns the next package of table rows for continuos scrolling.
    """
    failure = {
        "status" : "error",
        "message": "Nothing found."
    }
    if not ids and not show_all:
        # return json.dumps(failure)
        return {}
    dic = structures.get_all_structures_as_dict(ids, show_all)
    number = len(dic)
    print("--> Got {} structures from actual search.".format(number))
    if number == 0:
        # return json.dumps(failure)
        return {}
    return {"total": number, "records": dic, "status": "success"}


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
            <div style="font-size:0pt" id='hidden-cell'>{0}  {1}  {2}  {3}  {4}  {5}</div>
            """.format(c[0], c[1], c[2], c[3], c[4], c[5], round(c[6], 2))
    return cstr


def get_residuals_table1(structures: StructureTable, cif_dic: dict, structure_id: int) -> str:
    """
    Returns a table with the most important residuals of a structure.
    """
    try:
        rsigma = " / {}".format(cif_dic['_diffrn_reflns_av_unetI_netI'])
    except (TypeError, ValueError):
        rsigma = " "
    if not cif_dic:
        return ""
    if cif_dic['_refine_diff_density_max']:
        peakhole = "{} / {}".format(cif_dic['_refine_diff_density_max'], cif_dic['_refine_diff_density_min'])
    else:
        peakhole = " "
    try:
        sumform = format_sum_formula(structures.get_calc_sum_formula(structure_id), break_after=99)
    except KeyError:
        sumform = ''
    if sumform == '':
        # Display this as last resort:
        sumform = cif_dic['_chemical_formula_sum']
    table1 = """
    <table class="table table-bordered table-condensed" id='resitable1'>
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
        <tr><td><b><i>R</i><sub>int</sub> / <i>R</i><sub>&sigma;</sub></b></b></td>    <td>{9}{10} </td></tr>
        <tr><td><b>Wavelength [&angst;]</b></td>                      <td>{11}</td></tr>
        </tbody>
    </table>
    """.format(cif_dic['_space_group_name_H_M_alt'],
               cif_dic['_cell_formula_units_Z'],
               sumform,
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
        if isinstance(compl, str):
            compl = 0.0
    except TypeError:
        compl = 0.0
    try:
        data_to_param = cif_dic['_refine_ls_number_reflns'] / cif_dic['_refine_ls_number_parameters']
    except TypeError:
        data_to_param = 0
    table2 = """
    <table class="table table-bordered table-condensed" id='resitable2'>
        <tbody>
        <tr><td style='width: 40%'><b>Measured Refl.</b></td>       <td>{0}</td></tr>
        <tr><td><b>Independent Refl.</b></td>                       <td>{9}</td></tr>
        <tr><td><b>Data with [<i>I</i>>2&sigma;(<i>I</i>)] </b></td>    <td>{10}</td></tr>
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
                        <table class="table table-striped table-bordered table-condensed" style="white-space: pre">
                            <thead>
                                <tr>
                                    <th> Item </th>
                                    <th> Value </th>
                                </tr>
                            </thead>
                        <tbody>"""
    # get the residuals of the cif file as a dictionary:
    dic = structures.get_row_as_dict(structure_id)
    if not dic:
        return ""
    # filling table with data rows:
    for key, value in dic.items():
        if key == "Id":
            continue
        if isinstance(value, str):
            value = ''.join([x.replace("\n", "<br>").rstrip('\r\n') for x in value])
        if key == '_shelx_res_file':
            # Adding an ID to make font monospace in the view:
            table_string += '''<tr>
                                 <td class="residual-{}"> {} </a></td> 
                                 <td id=resfile > {} </a></td> 
                               </tr> \n'''.format(structure_id, key, value)
        else:
            table_string += '''<tr>
                                <td class="residual-{}"> {} </a></td> 
                                <td> {} </a></td> 
                           </tr> \n'''.format(structure_id, key, value)
    # closing table:
    table_string += """ </tbody>
                        </table>
                        </div>"""
    return table_string


def chunks(l: list, n: int) -> list:
    """
    returns successive n-sized chunks from l.
    >>> l = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 'a', 'b', 'c', 'd', 'e', 'f']
    >>> chunks(l, 5)
    [[1, 2, 3, 4, 5], [6, 7, 8, 9, 0], ['a', 'b', 'c', 'd', 'e'], ['f']]
    >>> chunks(l, 1)
    [[1], [2], [3], [4], [5], [6], [7], [8], [9], [0], ['a'], ['b'], ['c'], ['d'], ['e'], ['f']]
    >>> chunks(l, 50)
    [[1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 'a', 'b', 'c', 'd', 'e', 'f']]
    """
    return [l[i:i + n] for i in range(0, len(l), n)]


def find_cell(structures: StructureTable, cell: list, sublattice=False, more_results=False) -> list:
    """
    Finds unit cells in db. Rsturns hits a a list of ids.
    """
    if more_results:
        # more results:
        vol_threshold = 0.09
        ltol = 0.2
        atol = 2
    else:
        # regular:
        vol_threshold = 0.03
        ltol = 0.06
        atol = 1
    volume = lattice.vol_unitcell(*cell)
    idlist = structures.find_by_volume(volume, vol_threshold)
    if sublattice:
        # sub- and superlattices:
        for v in [volume * x for x in [2.0, 3.0, 4.0, 6.0, 8.0, 10.0]]:
            # First a list of structures where the volume is similar:
            idlist.extend(structures.find_by_volume(v, vol_threshold))
        idlist = list(set(idlist))
        idlist.sort()
    idlist2 = []
    # Real lattice comparing in G6:
    if idlist:
        try:
            lattice1 = mat_lattice.Lattice.from_parameters_niggli_reduced(*cell)
        except ValueError:
            lattice1 = mat_lattice.Lattice.from_parameters(*cell)
        cells = []
        # SQLite can only handle 999 variables at once:
        for cids in chunks(idlist, 500):
            cells.extend(structures.get_cells_as_list(cids))
        for num, cell_id in enumerate(idlist):
            try:
                lattice2 = mat_lattice.Lattice.from_parameters(*cells[num][:6])
            except ValueError:
                continue
            mapping = lattice1.find_mapping(lattice2, ltol, atol, skip_rotation_matrix=True)
            if mapping:
                idlist2.append(cell_id)
    if idlist2:
        return idlist2
    else:
        return []


def search_text(structures: StructureTable, search_string: str) -> tuple:
    """
    searches db for given text
    """
    idlist = []
    if len(search_string) == 0:
        return ()
    if len(search_string) >= 2:
        if "*" not in search_string:
            search_string = "{}{}{}".format('*', search_string, '*')
    try:
        #  bad hack, should make this return ids like cell search
        idlist = tuple([x[0] for x in structures.find_by_strings(search_string)])
    except AttributeError as e:
        print("Exception in search_text:")
        print(e)
    return idlist


def search_elements(structures: StructureTable, elements: str, excluding: str = '', onlyelem: bool = False) -> list:
    """
    list(set(l).intersection(l2))
    """
    res = []
    try:
        formula = get_list_of_elements(elements)
    except KeyError:
        print('Element search error! Wrong list of elements.')
        return []
    try:
        formula_ex = get_list_of_elements(excluding)
    except KeyError:
        print('Error: Wrong list of Elements!')
        return []
    try:
        res = structures.find_by_elements(formula, excluding=formula_ex, onlyincluded=onlyelem)
    except AttributeError:
        print('Element search error! Wrong list of elements..')
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
                    date1: str = None, date2: str = None, structures: StructureTable = None,
                    it_num: str = None, onlythese: bool = False) -> list:
    """
    Combines all the search fields. Collects all includes, all excludes ad calculates
    the difference.
    """
    #
    results = []
    cell_results = []
    spgr_results = []
    elincl_results = []
    txt_results = []
    txt_ex_results = []
    date_results = []
    cell = is_valid_cell(cellstr)
    try:
        spgr = int(it_num.split()[0])
    except:
        spgr = 0
    if cell:
        cell_results = find_cell(structures, cell, sublattice=sublattice, more_results=more_results)
    if spgr:
        spgr_results = structures.find_by_it_number(spgr)
    if elincl or elexcl:
        elincl_results = search_elements(structures, elincl, elexcl, onlythese)
    if txt:
        txt_results = [i[0] for i in structures.find_by_strings(txt)]
    if txt_ex:
        txt_ex_results = [i[0] for i in structures.find_by_strings(txt_ex)]
    if date1 != date2:
        date_results = find_dates(structures, date1, date2)
    ####################
    results = combine_results(cell_results, date_results, elincl_results, results, spgr_results,
                              txt_ex_results, txt_results)
    return flatten(list(results))


if __name__ == "__main__":
    print("Running on Python version {}".format(sys.version))
    if not is_a_nonzero_file(dbfilename):
        print("Unable to start!")
        print("The database file '{}' does not exist.".format(os.path.abspath(dbfilename)))
        sys.exit()
    print('### Running with database "{}" ###'.format(os.path.abspath(dbfilename)))
    # plain python wsgiref server (gunicorn doesnt run on windows):
    # app.run(host=host, port=port, server='wsgiref', reloader=True)
    # gunicorn server: Best used behind an nginx proxy server: http://docs.gunicorn.org/en/stable/deploy.html
    # you need "pip3 install gunicorn" to run this:
    # The current database interface allows only one worker (have to go to sqlalchemy!)
    if sys.platform == 'win32':
        server = 'wsgiref'
    else:
        server = 'gunicorn'
    app.run(host=host, port=port, reload=True, server=server, accesslog='-', errorlog='-', workers=1,
            access_log_format='%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s"')
