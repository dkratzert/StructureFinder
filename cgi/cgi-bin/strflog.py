#!C:\tools\Python-3.6.2_64\python.exe
##!/usr/local/bin/python3

import pathlib
from string import Template
from urllib import parse
from wsgiref.util import setup_testing_defaults

from lattice import lattice
from pymatgen.core import mat_lattice
from searcher import database_handler


# cgitb.enable(display=1, logdir="./log")
from searcher.database_handler import StructureTable


def application(environ, start_response):
    """
    The main application of the StructureFinder web interface.
    """
    setup_testing_defaults(environ)
    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0
    # When the method is POST the variable will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.
    # pprint.pprint(environ)
    request_body = environ['wsgi.input'].read(request_body_size).decode('utf-8')
    d = parse.parse_qs(request_body)
    dbfilename = "./structuredb.sqlite"
    structures = database_handler.StructureTable(dbfilename)
    # pprint.pprint('request_body:', d)
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=utf-8')]
    start_response(status, headers)
    if d.get("cell"):
        cell = (d.get("cell")[0])
        ids = find_cell(structures, cell)
        html = process_data(structures, ids)
        return [html]
    if d.get("txtsearch"):
        txt = (d.get("txtsearch")[0])
        ids_txt = search_text(structures, txt)
        html = process_data(structures, ids_txt)
        return [html]
    print(d.get("tst"))
    txt = process_data(structures)
    return [txt]


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


def process_data(structures: StructureTable, idlist: list=None):
    """
    Structure.Id,           0
    Structure.measurement,  1
    Structure.path,         2
    Structure.filename,     3
    Structure.dataname      4
    """
    print("process data ###")
    if not structures:
        return []
    table_string = ""
    for i in structures.get_all_structure_names(idlist):
        table_string += '<tr> <td> <a href="{3}"> {0} </a></td> ' \
                        '     <td> <a href=""> {1} </a></td> ' \
                        '     <td> <a href=""> {2} </a></td> </tr> \n' \
                            .format(i[3].decode('utf-8', errors='ignore'),
                                    i[4].decode('utf-8', errors='ignore'),
                                    i[2].decode('utf-8', errors='ignore'),
                                    i[0]
                                    )
        # i[0] -> id
    p = pathlib.Path("./cgi/strflog_Template.htm")
    t = Template(p.read_bytes().decode('utf-8', 'ignore'))
    replacedict = {"logtablecolumns": table_string, "CSearch": "Search", "TSearch": "Search"}
    return str(t.safe_substitute(replacedict)).encode('utf-8', 'ignore')


if __name__ == "__main__":
    try:
        import wsgiref.simple_server

        server = wsgiref.simple_server.make_server('127.0.0.1', 8000, application)
        server.serve_forever()
        print("Webserver running...")
    except KeyboardInterrupt:
        print("Webserver stopped...")
