import datetime
import math
import os
import sys
from argparse import ArgumentParser
from pathlib import Path
from shutil import which
from xml.etree.ElementTree import ParseError

import gemmi

from structurefinder.ccdc.query import get_cccsd_path, parse_results, search_csd
from structurefinder.displaymol.mol_file_writer import MolFile
from structurefinder.displaymol.sdm import SDM
from structurefinder.misc.exporter import cif_data_to_document
from structurefinder.misc.version import VERSION
from structurefinder.pymatgen.core import lattice
from structurefinder.searcher.constants import (
    centering_letter_2_num,
    centering_num_2_letter,
)
from structurefinder.searcher.database_handler import StructureTable
from structurefinder.searcher.misc import (
    combine_results,
    format_sum_formula,
    get_list_of_elements,
    is_a_nonzero_file,
    is_valid_cell,
    more_results_parameters,
    regular_results_parameters,
    vol_unitcell,
)

parser = ArgumentParser(prog='strf_web',
                        description=f'StructureFinder Web Server v{VERSION}')
parser.add_argument('-n', '--host', default='127.0.0.1', type=str, dest='host')
parser.add_argument('-p', '--port', default='8080', type=str, dest='port')
parser.add_argument('-f', '--dbfile', default='structuredb.sqlite', dest='dbfilename')
parser.add_argument('-d', '--download', dest='download_button', action='store_true',
                    help='Shows a download link in the page bottom')
args = parser.parse_args()

host = args.host
port = args.port
# Give an absolute path:
dbfilename = Path(args.dbfilename).resolve()
download_button = args.download_button

###########################################################

site_ip = host + ':' + port
os.chdir(Path(__file__).parent.parent)
try:  # Adding local path to PATH
    sys.path.insert(0, os.path.abspath('.'))
except(KeyError, ValueError):
    print('Unable to set PATH properly. strf_web.py might not work.')

pyver = sys.version_info
if pyver[0] == 3 and pyver[1] < 4:
    # Python 2 creates a syntax error anyway.
    print("You need Python 3.4 and up in oder to run this program!")
    sys.exit()

from structurefinder.cgi_ui.bottle import (
    Bottle,
    HTTPResponse,
    redirect,
    request,
    response,
    static_file, template,
)

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
    data = {"my_ip"        : site_ip,
            "title"        : 'StructureFinder',
            'host'         : host,
            'download_link': rf"""<p><a href="http://{site_ip}/dbfile.sqlite" download="structurefinder.sqlite" 
                                     type="application/*">Download
                                    database file</a></p>""" if download_button else ''
            }
    output = template('cgi_ui/views/strf_web', data)
    return output


@app.get('/dbfile.sqlite')
def get_dbfile():
    if download_button:
        return Path(dbfilename).read_bytes()
    else:
        return error404('File not found.')


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
        print(f"--> Got {len(ids)} structures from cell search.")
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
    r1val = request.GET.r1val
    ccdc_num = request.GET.ccdc_num
    structures = StructureTable(dbfilename)
    print("Advanced search: elin:", elincl, 'elout:', elexcl, date1, '|', date2, '|', cell_search, 'txin:', txt_in,
          'txout:', txt_out, '|', 'more:', more_results, 'Sublatt:', sublattice, 'It-num:', it_num, 'only:', onlyelem,
          'CCDC:', ccdc_num)
    ids = advanced_search(cellstr=cell_search, elincl=elincl, elexcl=elexcl, txt=txt_in, txt_ex=txt_out,
                          sublattice=sublattice, more_results=more_results, date1=date1, date2=date2,
                          structures=structures, it_num=it_num, onlythese=onlyelem, r1val=r1val, ccdc_num=ccdc_num)
    print(f"--> Got {len(ids)} structures from Advanced search.")
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
            atoms = structures.get_atoms_table(str_id, cartesian=False, as_list=True)
            if atoms:
                sdm = SDM(atoms, symmcards, cell)
                needsymm = sdm.calc_sdm()
                atoms = sdm.packer(sdm, needsymm)
        else:
            atoms = structures.get_atoms_table(str_id, cartesian=True, as_list=False)
        try:
            m = MolFile(atoms)
            return m.make_mol()
        except(KeyError, TypeError) as e:
            print(f'Exception in jsmol_request: {e}')
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


# noinspection PyUnresolvedReferences
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
    from structurefinder.misc.version import VERSION
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


@app.route('/current-cif/<structure_id:int>')
def download_currently_selected_cif(structure_id):
    if not download_button:
        return 'Downloading a CIF was turned off by the administrator.'
    headers = {}
    structures = StructureTable(dbfilename)
    cif_data = structures.get_cif_export_data(structure_id)
    doc = cif_data_to_document(cif_data)
    options = gemmi.cif.WriteOptions()
    options.align_pairs = 35
    file = doc.as_string(options=options)
    headers['Content-Type'] = 'text/plain'
    headers['Content-Encoding'] = 'ascii'
    headers['Content-Length'] = len(file)
    now = datetime.datetime.now()
    lm = now.strftime("%a, %d %b %Y %H:%M:%S GMT")
    headers['Last-Modified'] = lm
    return HTTPResponse(file, **headers)


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
        cellstr = '{:>8.3f} {:>8.3f} {:>8.3f} {:>8.3f} {:>8.3f} {:>8.3f}'.format(*cell)
    else:
        cellstr = ''
    if centering:
        try:
            cent = centering_letter_2_num[centering]
        except KeyError:  # mostly value of '?'
            cent = 0
    else:
        cent = 0
    response.content_type = 'text/html; charset=UTF-8'
    data = {"my_ip"  : site_ip,
            "title"  : 'StructureFinder',
            'cellstr': cellstr,
            'strid'  : str_id,
            'cent'   : cent,
            'host'   : host, }
    output = template('cgi_ui/views/cellcheckcsd', data)
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
        print(len(results), 'Structures found...')
        return {"total": len(results), "records": results, "status": "success"}
    else:
        return {}


@app.error(404)
def error404(error='Nothing here, sorry.'):
    """
    Redefine 404 message.
    """
    return f'''<div style="text-align: center;">
                <b>{error}</b><br>
                <p>
                <a href="http://{host}:{port}/">Back to main page</a>
                </p>
              </div>
            '''


def is_ajax():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return True
    else:
        return False


def get_structures_json(structures: StructureTable, ids: list | tuple | None = None, show_all: bool = False) -> dict:
    """
    Returns the next package of table rows for continuos scrolling.
    """
    if not ids and not show_all:
        return {}
    dic = structures.get_all_structures_as_dict(ids)
    number = len(dic)
    print(f"--> Got {number} structures from actual search.")
    if number == 0:
        return {}
    return {"total": number, "records": dic, "status": "success"}


def get_cell_parameters(structures: StructureTable, strid: str) -> str:
    """
    Resturns unit cell parameters as html formated string.
    """
    c = structures.get_cell_by_id(strid)
    cstr = f"""<b>Unit Cell:</b>&nbsp;&nbsp; 
                      <i>a</i> = {c[0]:>8.3f}&nbsp;&angst;,&nbsp;
                      <i>b</i> = {c[1]:>8.3f}&nbsp;&angst;,&nbsp;
                      <i>c</i> = {c[2]:>8.3f}&nbsp;&angst;,&nbsp; 
                      <i>&alpha;</i> = {c[3]:>8.3f}&deg;,&nbsp;
                      <i>&beta;</i> = {c[4]:>8.3f}&deg;,&nbsp;
                      <i>&gamma;</i> = {c[5]:>8.3f}&deg;,&nbsp;
                      <i>V</i> = {round(c[6], 2)}&nbsp;&angst;<sup>3</sup>&nbsp;&nbsp;&nbsp;&nbsp; 
            <div style="font-size:0pt" id='hidden-cell'>{c[0]}  {c[1]}  {c[2]}  {c[3]}  {c[4]}  {c[5]}</div>
            """
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
        <tr><td style='width: 40%'><b>Space Group</b></td>                 <td>{}</td></tr>
        <tr><td><b>Z</b></td>                           <td>{}</td></tr>
        <tr><td><b>Sum Formula</b></td>                 <td>{}</td></tr>
        <tr><td><b>Temperature [K]</b></td>             <td>{}</td></tr>
        <tr><td><b><i>wR</i><sub>2</sub></b></td>       <td>{}</td></tr>
        <tr><td><b><i>R<i/><sub>1</sub></b></td>        <td>{}</td></tr>
        <tr><td><b>Goof</b></td>                        <td>{}</td></tr>
        <tr><td><b>Max Shift/esd</b></td>               <td>{}</td></tr>
        <tr><td><b>Peak / Hole [e&angst;<sup>&minus;3</sup>]</b></td>             <td>{}</td></tr>
        <tr><td><b><i>R</i><sub>int</sub> / <i>R</i><sub>&sigma;</sub></b></b></td>    <td>{}{} </td></tr>
        <tr><td><b>Wavelength [&angst;]</b></td>                      <td>{}</td></tr>
        </tbody>
    </table>
    """.format(cif_dic['_space_group_name_H_M_alt'],
               cif_dic['_cell_formula_units_Z'],
               sumform,
               cif_dic['_diffrn_ambient_temperature'],
               cif_dic['_refine_ls_wR_factor_ref'] if cif_dic['_refine_ls_wR_factor_ref'] else cif_dic[
                   '_refine_ls_wR_factor_gt'],
               cif_dic['_refine_ls_R_factor_gt'] if cif_dic['_refine_ls_R_factor_gt'] else cif_dic[
                   '_refine_ls_R_factor_all'],
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
    if not cif_dic:
        return ""
    wavelen = cif_dic['_diffrn_radiation_wavelength']
    thetamax = cif_dic['_diffrn_reflns_theta_max']
    thetafull = cif_dic['_diffrn_reflns_theta_full']
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
        <tr><td style='width: 40%'><b>Measured Refl.</b></td>       <td>{}</td></tr>
        <tr><td><b>Independent Refl.</b></td>                       <td>{}</td></tr>
        <tr><td><b>Data with [<i>I</i>>2&sigma;(<i>I</i>)] </b></td>    <td>{}</td></tr>
        <tr><td><b>Parameters</b></td>                              <td>{}</td></tr>
        <tr><td><b>data/param</b></td>                              <td>{:<5.1f}</td></tr>
        <tr><td><b>Restraints</b></td>                              <td>{}</td></tr>
        <tr><td><b>&theta;<sub>full</sub> [&deg;]</b> / 
        <b>&theta;<sub>max</sub> [&deg;]</b></td>                    <td>{} / {}</td></tr>
        <tr><td><b>d [&angst;]</b></td>                             <td>{:5.3f}</td></tr>
        <tr><td><b>completeness [%]</b></td>                            <td>{:<5.1f}</td></tr>
        <tr><td><b>Flack X parameter</b></td>                             <td>{}</td></tr>
        <tr><td><b>CCDC Number</b></td>                             <td>{}</td></tr>
        </tbody>
    </table>
    """.format(cif_dic['_diffrn_reflns_number'],  # 0
               cif_dic['_refine_ls_number_reflns'],  # 1
               cif_dic['_reflns_number_gt'],  # 2
               cif_dic['_refine_ls_number_parameters'],  # 3
               data_to_param,  # 4
               cif_dic['_refine_ls_number_restraints'],  # 5
               thetamax if thetamax else '?',  # 6
               thetafull if thetafull else '?',  # 7
               d,  # 8
               compl,  # 9
               cif_dic['_refine_ls_abs_structure_Flack'],  # 10
               cif_dic['_database_code_depnum_ccdc_archive']  # 11
               )
    return table2


def get_all_cif_val_table(structures: StructureTable, structure_id: int) -> str:
    """
    Returns a html table with the residuals values of a structure.
    """
    # starting table header (the div is for css):
    # style="white-space: pre": preserves white space
    button = f"""<a type="button" class="btn btn-default btn-sm" id="download_CIF"
                                                 href='current-cif/{structure_id}' >Download as CIF</a>"""
    table_string = """<h4>All CIF values</h4> {}
                        <div id="myresidualtable">
                        <table class="table table-striped table-bordered table-condensed" style="white-space: pre">
                            <thead>
                                <tr>
                                    <th> Item </th>
                                    <th> Value </th>
                                </tr>
                            </thead>
                        <tbody>""".format(button if download_button else '')
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
            table_string += f'''<tr>
                                 <td class="residual-{structure_id}"> {key} </a></td> 
                                 <td id=resfile > {value} </a></td> 
                               </tr> \n'''
        else:
            table_string += f'''<tr>
                                <td class="residual-{structure_id}"> {key} </a></td> 
                                <td> {value} </a></td> 
                           </tr> \n'''
    # closing table:
    table_string += """ </tbody>
                        </table>
                        </div>"""
    return table_string


def chunks(l: list, n: int) -> list:
    """
    returns successive n-sized chunks from l.
    """
    return [l[i:i + n] for i in range(0, len(l), n)]


def find_cell(structures: StructureTable, cell: list, sublattice=False, more_results=False) -> list:
    """
    Finds unit cells in db. Rsturns hits a a list of ids.
    """
    volume = vol_unitcell(*cell)
    if more_results:
        # more results:
        atol, ltol, vol_threshold = more_results_parameters(volume)
    else:
        # regular:
        atol, ltol, vol_threshold = regular_results_parameters(volume)
    cells: list = structures.find_by_volume(volume, vol_threshold)
    if sublattice:
        # sub- and superlattices:
        for v in [volume * x for x in [2.0, 3.0, 4.0, 6.0, 8.0, 10.0]]:
            # First a list of structures where the volume is similar:
            cells.extend(structures.find_by_volume(v, vol_threshold))
        cells = list(set(cells))
    idlist2: list = []
    # Real lattice comparing in G6:
    if cells:
        lattice1 = lattice.Lattice.from_parameters(*cell)
        for num, curr_cell in enumerate(cells):
            try:
                lattice2 = lattice.Lattice.from_parameters(*curr_cell[1:7])
            except ValueError:
                continue
            mapping = lattice1.find_mapping(lattice2, ltol, atol, skip_rotation_matrix=True)
            if mapping:
                idlist2.append(curr_cell[0])
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
    if len(search_string) >= 2 and "*" not in search_string:
        search_string = "{}{}{}".format('*', search_string, '*')
    try:
        #  bad hack, should make this return ids like cell search
        idlist = structures.find_text_and_authors(search_string)
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
                    date1: str | None = None, date2: str | None = None, structures: StructureTable = None,
                    it_num: str | None = None, onlythese: bool = False, r1val: float = 0.0,
                    ccdc_num: str = '') -> list[int] | tuple[int, ...]:
    """
    Combines all the search fields. Collects all includes, all excludes ad calculates
    the difference.
    """
    results: list = []
    cell_results: list = []
    spgr_results: list = []
    elincl_results: list = []
    txt_results: list | tuple = []
    txt_ex_results: list | tuple = []
    date_results: list = []
    ccdc_num_results: list = []
    states: dict[str, bool] = {'date'    : False,
                               'cell'    : False,
                               'elincl'  : False,
                               'elexcl'  : False,
                               'txt'     : False,
                               'txt_ex'  : False,
                               'spgr'    : False,
                               'rval'    : False,
                               'ccdc_num': False,
                               }
    if ccdc_num:
        ccdc_num_results = structures.find_by_ccdc_num(ccdc_num)
    if ccdc_num_results:
        return ccdc_num_results
    cell = is_valid_cell(cellstr)
    try:
        spgr = int(it_num.split()[0])
    except Exception:
        spgr = 0
    try:
        rval = float(r1val)
        states['rval'] = True
    except ValueError:
        rval = 0.0
    if cell:
        states['cell'] = True
        cell_results = find_cell(structures, cell, sublattice=sublattice, more_results=more_results)
    if spgr:
        states['spgr'] = True
        spgr_results = structures.find_by_it_number(spgr)
    if elincl or elexcl:
        if elincl:
            states['elincl'] = True
        if elexcl:
            states['elexcl'] = True
        elincl_results = search_elements(structures, elincl, elexcl, onlythese)
    if txt:
        states['txt'] = True
        txt_results = structures.find_text_and_authors(txt)
    if txt_ex:
        states['txt_ex'] = True
        txt_ex_results = structures.find_text_and_authors(txt_ex)
    if date1 != date2:
        states['date'] = True
        date_results = find_dates(structures, date1, date2)
    rval_results = []
    if rval > 0.0:
        rval_results = structures.find_by_rvalue(rval / 100)
    ####################
    results = combine_results(cell_results=cell_results,
                              date_results=date_results,
                              elincl_results=elincl_results,
                              results=results,
                              spgr_results=spgr_results,
                              txt_ex_results=txt_ex_results,
                              txt_results=txt_results,
                              rval_results=rval_results,
                              states=states)
    return list(results)


def run():
    print(f"----- StructureFinder web application version {sys.version} --------------")
    print(f" Running on Python version {sys.version}")
    if not is_a_nonzero_file(dbfilename):
        print("Unable to start!")
        print(f"The database file '{os.path.abspath(dbfilename)}' does not exist.")
        sys.exit()
    print(f'### Running with database "{os.path.abspath(dbfilename)}" ###')
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


if __name__ == "__main__":
    run()
