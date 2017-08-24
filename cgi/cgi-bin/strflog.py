#!C:\tools\Python-3.6.2_64\python.exe
##!/usr/local/bin/python3

import os
import pprint
from html import escape
from urllib import parse
from string import Template
import cgitb
import datetime
import sys
from wsgiref.util import setup_testing_defaults, FileWrapper

import pathlib

from searcher import database_handler

cgitb.enable(display=1, logdir="./log")


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
    #pprint.pprint(environ)
    request_body = environ['wsgi.input'].read(request_body_size).decode('utf-8')
    d = parse.parse_qs(request_body)
    #pprint.pprint('request_body:', d)
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=utf-8')]
    start_response(status, headers)
    txt = process_data()
    return [txt]


def process_data(dbfilename="./structuredb.sqlite"):
    """
    Structure.Id             0
    Structure.measurement    1
    Structure.path           2
    Structure.filename       3
    Structure.dataname       4
    """
    structures = database_handler.StructureTable(dbfilename)
    if not structures:
        return []
    table_string = ""
    for i in structures.get_all_structure_names():
        line = '<tr> <td>{0}</td> <td>{1}</td> <td>{2}</td> <td>{3}</td> </tr>\n'\
                .format(i[3].decode('ascii', errors='ignore'),
                        i[4].decode('ascii', errors='ignore'),
                        i[2].decode('ascii', errors='ignore'),
                        i[0]
                        )
        # i[0] -> id
        table_string += line
        table_string = table_string
    p = pathlib.Path("./cgi/strflog_Template.htm")
    t = Template(p.read_bytes().decode('utf-8', 'ignore'))
    return str(t.safe_substitute({"logtablecolumns": table_string})).encode('utf-8', 'ignore')#.decode('utf-8')


if __name__ == "__main__":
    try:
        import wsgiref.simple_server
        server = wsgiref.simple_server.make_server('127.0.0.1', 8000, application)
        server.serve_forever()
        print("Webserver running...")
    except KeyboardInterrupt:
        print("Webserver stopped...")
