#!/usr/bin/python3

import cgi
import os
import sqlite3
from string import Template
import cgitb
import datetime
import sys


cgitb.enable(display=0, logdir="/path/to/logdir")


def main():

    form = cgi.FieldStorage()  # standard cgi script lines to here!
    # Daten aus den Forms auslesen

    mytitlesearchstring = form.getfirst("titlesearchstring", "*")  # Use default "*" if there is none.
    myusersearchstring = form.getfirst("usersearchstring", "*")  # Use default "*" if there is none.
    mymachinesearchstring = form.getfirst("machinesearchstring", "*")  # Use default "*" if there is none.
    mynucsearchstring = form.getfirst("nucsearchstring", "*")  # Use default "*" if there is none.
    mypulprogsearchstring = form.getfirst("pulprogsearchstring", "*")  # Use default "*" if there is none.

    contents = processInput(mytitlesearchstring, myusersearchstring,
                            mymachinesearchstring, mynucsearchstring,
                            mypulprogsearchstring)  # process input into a page

    print(contents)


def processInput(mytitlesearchstring, myusersearchstring, mymachinesearchstring, mynucsearchstring,
                 mypulprogsearchstring):
    """
    Process input parameters and return the final page as a string.
    """
    dbname = 'nmrlogdatabase111.db'
    farben = ('#FFFFFF', '#B7D1E6')

    dboutput = nmrlogquery(dbname, mytitle=mytitlesearchstring,
                           myuser=myusersearchstring, mymachine=mymachinesearchstring,
                           mynuc=mynucsearchstring, mypulprog=mypulprogsearchstring)
    # make actual table from resulting lines
    mlogtablecolumns = ''

    for zaehler, line in enumerate(dboutput):
        mlogtablecolumns += '<tr>'
        horst = line[0]
        fullpath = line[10]
        parameters = (
        ' td={0}\n td1={1}\n bf1={2}\n o1={3}\n lock={4}\n sw={5}\n sw1={6}\n te={7}\n probe={8}\n p1={9}\n p2={10}\n p3={11}').format(
                line[11], line[12], line[13], line[14], line[15], line[16], line[17], line[18], line[19], line[20],
                line[21], line[22])
        line = (horst[0:10],) + line[1:10]
        for nentry, myentry in enumerate(line):
            if nentry == 0:
                mlogtablecolumns += (
                '<td title = {0} style="background-color: ' + farben[zaehler % 2] + '">{1}&nbsp</td>').format(
                        horst[11:16], myentry)  # title in title for mouseover
            elif nentry == 1:
                mlogtablecolumns += (
                '<td title = {0} style="background-color: ' + farben[zaehler % 2] + '">{1}&nbsp</td>').format(fullpath,
                                                                                                              myentry)  # title in title for mouseover
            elif nentry == 6:
                mlogtablecolumns += (
                '<td title = "{0}" style="background-color: ' + farben[zaehler % 2] + '">{1}&nbsp</td>').format(
                    parameters, myentry)  # parameters in title for mouseover
            else:
                mlogtablecolumns += ('<td style="background-color: ' + farben[zaehler % 2] + '">{0}&nbsp</td>').format(
                    myentry)
        mlogtablecolumns += '</tr>'

    # mlogtablecolumns=mlogtablecolumns.encode('ASCII','ignore')

    # make selectors with preselection

    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute('SELECT DISTINCT nuc FROM nmrlog ORDER BY nuc')
    allnuc = c.fetchall()
    c.execute('SELECT DISTINCT pulprog FROM nmrlog ORDER BY pulprog')
    allpulprog = c.fetchall()
    #    c.execute('SELECT DISTINCT machine FROM nmrlog ORDER BY machine')
    #    allmachine=c.fetchall()
    c.execute('SELECT DISTINCT userdirname FROM nmrlog ORDER BY userdirname')
    alluser = c.fetchall()
    conn.close()

    allmachine = ['nmr200', 'nmr300', 'nmr400', 'dsx500']

    mynucselector = makeselector([(x[0]) for x in allnuc], mynucsearchstring)
    mypulprogselector = makeselector([(x[0]) for x in allpulprog], mypulprogsearchstring)
    mymachineselector = makeselector(allmachine, mymachinesearchstring)
    myuserselector = makeselector([(x[0]) for x in alluser], myusersearchstring)
    templatetext = fileToStr('nmrlog_Template.htm')
    sitetemplate = Template(templatetext)
    contents = sitetemplate.safe_substitute(logtablecolumns=mlogtablecolumns,
                                            usersearchstring=myusersearchstring,
                                            titlesearchstring=mytitlesearchstring,
                                            startsearchstring=mystart,
                                            endsearchstring=myend,
                                            nucselector=mynucselector,
                                            pulprogselector=mypulprogselector,
                                            userselector=myuserselector,
                                            machineselector=mymachineselector)
    return contents.encode(encoding="utf-8", errors="ignore").decode(encoding='ascii', errors='ignore')


def nmrlogquery(dbfilename, mystart, myend, mymachine='*',
                myuser='*', mynuc='*', mypulprog='*', mytitle='*'):
    conn = sqlite3.connect(dbfilename)
    c = conn.cursor()
    # Anfueringsuzeichen vorne und hinten anhaengen
    mystart = "\'" + mystart + "\'"
    myend = "\'" + myend + "\'"
    mymachine = "\'" + mymachine + "\'"
    myuser = "\'" + myuser + "\'"
    mynuc = "\'" + mynuc + "\'"
    mypulprog = "\'" + mypulprog + "\'"
    mytitle = "\'*" + mytitle + "*\'"
    # Datenbanksuche und sortieren au
    query = '''SELECT dateandtime, machine, userdirname,expname,expno, nuc,pulprog, ns, d1, title,fullpath,td,td1,bf1,o1,lock,sw,sw1,te,probe,p1,p2,p3 
        FROM nmrlog 
        WHERE dateandtime BETWEEN {0} AND {1} 
        AND machine GLOB {2}
        AND userdirname GLOB {3}
        AND nuc GLOB {4}
        AND pulprog GLOB {5}
        AND upper(title) GLOB upper({6}) 
        ORDER BY dateandtime DESC'''
    myquery = (query.format(mystart, myend, mymachine, myuser, mynuc, mypulprog, mytitle))
    c.execute(myquery)
    dboutput = c.fetchall()
    conn.close()
    return dboutput


def makeselector(mylist, selectedentry='*'):
    if selectedentry == '*':
        myselector = ('<option selected> * </option>')
    else:
        myselector = ('<option> * </option>')

    for myoption in mylist:
        if myoption == selectedentry:
            myselector += ('<option selected> {0} </option>').format(myoption)
        else:
            myselector += ('<option> {0} </option>').format(myoption)
    return myselector


# standard code for future cgi scripts from here on
def fileToStr(fileName):
    """Return a string containing the contents of the named file."""
    fin = open(fileName, 'r')
    contents = fin.read()
    fin.close()
    return contents


def strToFile(text, filename):
    """Write a file with the given name and the given text."""
    output = open(filename, "w")
    output.write(text)
    output.close()


try:  # NEW
    print("Content-type: text/html\n\n")  # say generating html
    main()
except:
    cgi.print_exception()  # catch and print errors
