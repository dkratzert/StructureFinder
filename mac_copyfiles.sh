#!/bin/bash

sudo cp -r cgi/jasny-bootstrap /Library/WebServer/CGI-Executables/
sudo cp -v cgi/cgi-bin/strflog.py /Library/WebServer/CGI-Executables/strflog.cgi
sudo cp -v cgi/strflog_Template.htm /Library/WebServer/Documents/