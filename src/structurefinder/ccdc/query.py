import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from pprint import pprint
from shutil import which
from tempfile import mkstemp
from typing import Union

from packaging.version import Version

DEBUG = False

try:
    from winreg import OpenKey, HKEY_CURRENT_USER, EnumKey, QueryInfoKey, EnumValue
except ImportError:
    pass

querytext = """<?xml version="1.0" encoding="UTF-8"?>
<query name="reduced_cell_search" version="1.0" originator="generic">
  <lattice_centring></lattice_centring>
  <a></a>
  <b></b>
  <c></c>
  <alpha></alpha>
  <beta></beta>
  <gamma></gamma>
  <settings>
    <dimension_tolerance>1.5</dimension_tolerance>
    <angle_tolerance>2.0</angle_tolerance>
    <maximum_hits>2000</maximum_hits>
  </settings>
</query> """


def get_cccsd_path() -> Union[Path, None]:
    r"""
    HKEY_CURRENT_USER\SOFTWARE\CCDC\CellCheckCSD
    """
    software = r'SOFTWARE\CCDC\CellCheckCSD\\'
    try:
        csd = OpenKey(HKEY_CURRENT_USER, software)
    except (FileNotFoundError, NameError):
        return None
    num = QueryInfoKey(csd)[0]  # returns the number of subkeys
    csd_path = None
    latest = Version('0.0')
    for n in range(num):
        vernum_dir = EnumKey(csd, n)  # subkey of version
        path = OpenKey(HKEY_CURRENT_USER, software + vernum_dir)
        ver = Version(vernum_dir)
        if QueryInfoKey(path)[1] > 0:  # subkey with content
            if latest < ver:
                csd_path = Path(EnumValue(path, 0)[1], 'ccdc_searcher.bat')
    if csd_path and csd_path.is_file():
        return csd_path
    else:
        try:
            if which('ccdc_searcher.bat'):
                return Path(which('ccdc_searcher.bat'))
            else:
                return Path(which('ccdc_searcher'))
        except TypeError:
            return None


def read_queryfile():
    """
    Reads a CellCheckCSD query file.
    """
    tree = ET.fromstring(querytext)
    return tree


def set_unitcell(cell: list, centering: str) -> ET:
    """
    Returns an xml query string for the CellCheckcsd -query option.
    """
    t = read_queryfile()
    cent = t.find('lattice_centring')
    a = t.find('a')
    b = t.find('b')
    c = t.find('c')
    alpha = t.find('alpha')
    beta = t.find('beta')
    gamma = t.find('gamma')
    a.text = str(cell[0])
    b.text = str(cell[1])
    c.text = str(cell[2])
    alpha.text = str(cell[3])
    beta.text = str(cell[4])
    gamma.text = str(cell[5])
    cent.text = centering
    return ET.tostring(t)


def parse_results(xmlinput: str) -> list:
    """
    Parses the search results into a dictionary.
    """
    root = ET.fromstring(xmlinput)
    results = []
    # each hit has a match:
    for num, r in enumerate(root.findall('match')):
        # The identifier is the csd entry name:
        ident = r.get('identifier')
        values = {'recid': ident}
        values['order'] = num
        # unit cells are listed in parameters:
        for p in r.findall('parameters'):
            for item in p.findall('parameter'):
                item_type = item.get('type')
                value = item.text
                values[item_type] = value
        results.append(values)
    return results


def search_csd(cell: list, centering: str, searcher_executable: str = '') -> str:
    querystring = set_unitcell(cell, centering).decode('utf-8')
    # prepare the temporary queryfile:
    querydescriptor, queryfile = mkstemp(suffix='xml')
    # prepare the temporary results file:
    resdescriptor, resultfile = mkstemp(suffix='xml')
    # write query to file:
    Path(queryfile).write_text(querystring)
    if sys.platform == 'win32':
        shell = True
    else:
        shell = False
    # Either use the path from the text field or from get_cccsd_path()
    if searcher_executable and Path(searcher_executable).exists() and Path(searcher_executable).is_file():
        path_to_exe = Path(searcher_executable)
    else:
        path_to_exe = get_cccsd_path()
    result_file = ''
    try:
        if DEBUG:
            print(f'Running CCDC query: {path_to_exe}')
        # run the search:
        # shell=True disables the output window of the process
        subprocess.run([str(path_to_exe.absolute()), '-query', queryfile, '-results', resultfile], shell=shell)
        # read the result:
        result_file = Path(resultfile).read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        print('Could not search cell:')
        print(e)
    os.close(resdescriptor)
    os.close(querydescriptor)
    try:
        os.remove(queryfile)
        os.remove(resultfile)
    except Exception:
        pass
    return result_file


if __name__ == '__main__':
    # print(get_cccsd_path())
    cell = [10.6369, 10.6369, 24.5938, 90.0, 90.0, 120.0]
    xml = search_csd(cell, centering='R')
    res = parse_results(xml)
    pprint(res)
