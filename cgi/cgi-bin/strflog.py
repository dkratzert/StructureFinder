#!C:\tools\Python-3.6.2_64\python.exe
##!/usr/local/bin/python3

import os
from html import escape
from urllib import parse
from string import Template
import cgitb
import datetime
import sys
from wsgiref.util import setup_testing_defaults

import pathlib

from searcher import database_handler

cgitb.enable(display=1, logdir="./log")


html = """
<html>
<body>
   <form method="post" action="">
        <p>
           Age: <input type="text" name="age" value="%(age)s">
        </p>
        <p>
            Hobbies:
            <input
                name="hobbies" type="checkbox" value="software"
                %(checked-software)s
            > Software
            <input
                name="hobbies" type="checkbox" value="tunning"
                %(checked-tunning)s
            > Auto Tunning
        </p>
        <p>
            <input type="submit" value="Submit">
        </p>
    </form>
    <p>
        Age: %(age)s<br>
        Hobbies: %(hobbies)s
    </p>
</body>
</html>
"""

def application(environ, start_response):
    """
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
    request_body = environ['wsgi.input'].read(request_body_size)
    d = parse.parse_qs(request_body)
    age = d.get(b'age', [''])[0]  # Returns the first age value.
    hobbies = d.get(b'hobbies', [])  # Returns a list of hobbies.
    # Always escape user input to avoid script injection
    try:
        age = escape(age.decode('ascii'))
        hobbies = [escape(hobby.decode('ascii')) for hobby in hobbies]
    except AttributeError:
        age = escape(age)
        hobbies = [escape(hobby) for hobby in hobbies]


    response_body = html % {  # Fill the above html template in
        'checked-software': ('', 'checked')['software' in hobbies],
        'checked-tunning' : ('', 'checked')['tunning' in hobbies],
        'age'             : age or 'Empty',
        'hobbies'         : ', '.join(hobbies or ['No Hobbies?'])
    }

    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=utf-8')]
    start_response(status, headers)
    #txt = process_data()

    return [response_body.encode('ascii')]


def process_data(dbfilename="../structuredb.sqlite"):
    """
    Structure.Id             0
    Structure.measurement    1
    Structure.path           2
    Structure.filename       3
    Structure.dataname       4
    """
    structures = database_handler.StructureTable(dbfilename)
    if not structures:
        return
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
    p = pathlib.Path("strflog_Template.htm")
    t = Template(p.read_bytes().decode('ascii', 'ignore'))
    return str(t.safe_substitute({"logtablecolumns": table_string})).encode('ascii', 'ignore')


if __name__ == "__main__":
    try:
        import wsgiref.simple_server
        server = wsgiref.simple_server.make_server('127.0.0.1', 8000, application)
        server.serve_forever()
        print("Webserver running...")
    except KeyboardInterrupt:
        print("Webserver stopped...")
