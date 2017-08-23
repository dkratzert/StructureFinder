#!/usr/local/bin/python3

import cgi
import os
import sqlite3
from string import Template
import cgitb
import datetime
import sys
from wsgiref.util import setup_testing_defaults, FileWrapper

import pathlib

cgitb.enable(display=1, logdir="./log")


def main(environ, start_response):
    """
    """
    setup_testing_defaults(environ)

    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, headers)
    ret = [("%s: %s\n" % (key, value)).encode("utf-8")
           for key, value in environ.items()]
    p = pathlib.Path("cgi/strflog_Template.htm")
    t = Template(p.read_text())
    f = p.open()
    wrapper = FileWrapper(b"foo", blksize=5)
    return [wrapper]


def process_data():
    """
    """
    p = pathlib.Path("cgi/strflog_Template.htm")
    t = Template(p.read_bytes())
    return t#.safe_substitute({"mlogtablecolumns":"9"})


if __name__ == "__main__":
try:
    import wsgiref.simple_server
    server = wsgiref.simple_server.make_server('127.0.0.1', 8000, main)
    server.serve_forever()
    print("Webserver running...")
except KeyboardInterrupt:
    print("Webserver stopped...")
