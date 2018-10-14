import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from tempfile import mktemp

querytext = """<?xml version="1.0" encoding="UTF-8"?>
<query name="reduced_cell_search" version="1.0" originator="StructureFinder">
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


def read_queryfile():
    """
    Reads a CellCheckCSD query file.
    """
    tree = ET.fromstring(querytext)
    return tree


def set_unitcell(cell: list, centering: str):
    t = read_queryfile()
    cent = t.find('lattice_centring')
    a = t.find('a')
    b = t.find('b')
    c = t.find('c')
    alpha = t.find('alpha')
    beta = t.find('beta')
    gamma = t.find('gamma')
    a = str(cell[0])
    b = str(cell[1])
    c = str(cell[2])
    alpha = str(cell[3])
    beta = str(cell[4])
    gamma = str(cell[5])
    cent = centering
    return ET.tostring(t)


def search_csd(cell: list, centering:str):
    querystring = set_unitcell(cell, centering)
    queryfile = mktemp(suffix='xml')
    resultfile = mktemp(suffix='xml')
    qf = Path(queryfile).write_text(querystring)
    # TODO: read path of executable from env
    p = Path('ccdc_searcher.bat')
    subprocess.run([p.resolve(), '-query', qf, '-results', resultfile])
    rf = Path(resultfile).read_text(encoding='utf-8', errors='ignore')
    return rf