#!C:\tools\Python-3.6.2_64\python.exe
##!/usr/local/bin/python3

import os
import sqlite3
from string import Template
import cgitb
import datetime
import sys
from wsgiref.util import setup_testing_defaults, FileWrapper

import pathlib

cgitb.enable(display=1, logdir="./log")


def application(environ, start_response):
    """
    """
    setup_testing_defaults(environ)

    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=utf-8')]
    start_response(status, headers)
    txt = process_data()
    return [txt]


def process_data():
    """
    """
    p = pathlib.Path("cgi/strflog_Template.htm")
    t = Template(p.read_bytes().decode('ascii', 'ignore'))
    return str(t.safe_substitute({"logtablecolumns":"9"})).encode('ascii', 'ignore')


if __name__ == "__main__":
    try:
        import wsgiref.simple_server
        server = wsgiref.simple_server.make_server('127.0.0.1', 8000, application)
        server.serve_forever()
        print("Webserver running...")
    except KeyboardInterrupt:
        print("Webserver stopped...")
