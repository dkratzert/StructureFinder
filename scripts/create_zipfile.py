"""
Creates a zip file with the content of the StructureDB program.
"""
from zipfile import ZipFile

import os

from misc.version import VERSION

version = VERSION

files = [
    "strf.py",
    "strf_cmd.py",
    "apex/__init__.py",
    "apex/apeximporter.py",
    "searcher/__init__.py",
    "searcher/atoms.py",
    "searcher/constants.py",
    "searcher/database_handler.py",
    "searcher/elements.py",
    "searcher/filecrawler.py",
    "searcher/fileparser.py",
    "searcher/misc.py",
    "searcher/spinner.py",
    "searcher/unitcell.py",
    "pymatgen/__init__.py",
    "pymatgen/core/__init__.py",
    "pymatgen/core/mat_lattice.py",
    "pymatgen/util/__init__.py",
    "pymatgen/util/num_utils.py",
    "lattice/__init__.py",
    "lattice/lattice.py",
    "pg8000/__init__.py",
    "pg8000/_version.py",
    "pg8000/core.py",
    "misc/__init__.py",
    "misc/update_check.py",
    "misc/version.py",
    "cgi_ui/bottle.py",
    "cgi_ui/__init__.py",
    "cgi_ui/cgi-bin/__init__.py",
    "cgi_ui/cgi-bin/strf_web.py",
    "cgi_ui/static/bootstrap-3.3.7/custom.css",
    "cgi_ui/static/bootstrap-3.3.7/css/bootstrap.css",
    "cgi_ui/static/bootstrap-3.3.7/css/bootstrap.css.map",
    "cgi_ui/static/bootstrap-3.3.7/css/bootstrap.min.css",
    "cgi_ui/static/bootstrap-3.3.7/css/bootstrap.min.css.map",
    "cgi_ui/static/bootstrap-3.3.7/css/bootstrap-theme.css",
    "cgi_ui/static/bootstrap-3.3.7/css/bootstrap-theme.css.map",
    "cgi_ui/static/bootstrap-3.3.7/css/bootstrap-theme.min.css",
    "cgi_ui/static/bootstrap-3.3.7/css/bootstrap-theme.min.css.map",
    "cgi_ui/static/bootstrap-3.3.7/css/font-awesome.css",
    "cgi_ui/static/bootstrap-3.3.7/fonts/FontAwesome.otf",
    "cgi_ui/static/bootstrap-3.3.7/fonts/fontawesome-webfont.eot",
    "cgi_ui/static/bootstrap-3.3.7/fonts/fontawesome-webfont.svg",
    "cgi_ui/static/bootstrap-3.3.7/fonts/fontawesome-webfont.ttf",
    "cgi_ui/static/bootstrap-3.3.7/fonts/fontawesome-webfont.woff",
    "cgi_ui/static/bootstrap-3.3.7/fonts/glyphicons-halflings-regular.eot",
    "cgi_ui/static/bootstrap-3.3.7/fonts/glyphicons-halflings-regular.svg",
    "cgi_ui/static/bootstrap-3.3.7/fonts/glyphicons-halflings-regular.ttf",
    "cgi_ui/static/bootstrap-3.3.7/fonts/glyphicons-halflings-regular.woff",
    "cgi_ui/static/bootstrap-3.3.7/fonts/glyphicons-halflings-regular.woff2",
    "cgi_ui/static/bootstrap-3.3.7/js/bootstrap.js",
    "cgi_ui/static/bootstrap-3.3.7/js/bootstrap.min.js",
    "cgi_ui/static/bootstrap-3.3.7/js/npm.js",
    "cgi_ui/static/clipboard/clipboard.js",
    "cgi_ui/static/clipboard/clipboard.min.js",
    "cgi_ui/static/favicon.ico",
    "cgi_ui/static/jquery/jquery-3.2.1.min.js",
    "cgi_ui/static/jsmol/JSmol_dk.nojq.lite.js",
    "cgi_ui/static/w2ui/w2ui-1.4.css",
    "cgi_ui/static/w2ui/w2ui-1.4.js",
    "cgi_ui/static/w2ui/w2ui-1.4.min.css",
    "cgi_ui/static/w2ui/w2ui-1.4.min.js",
    "cgi_ui/views/strf_web_template.tpl",
    "displaymol/__init__.py",
    "displaymol/jquery.min.js",
    "displaymol/jsmol.htm",
    "displaymol/jsmol-template.htm",
    "displaymol/JSmol_dk.nojq.lite.js",
    "displaymol/mol2_file_writer.py",
    "displaymol/mol_file_writer.py"
    ]


def make_zip(filelist):
    """
    :type filelist: list
    """
    os.chdir('../')
    with ZipFile('strf_cmd-v{}.zip'.format(version), mode='w',
                 allowZip64=False) as myzip:
        for f in filelist:
            print("Adding {}".format(f))
            myzip.write("StructureFinder/"+f)
    print("File written to {}".format(os.path.abspath('./')))

if __name__ == "__main__":
    make_zip(files)