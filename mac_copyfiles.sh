#!/bin/bash

sudo cp -r cgi_ui/jasny-bootstrap /Library/WebServer/CGI-Executables/
sudo cp -v cgi_ui/cgi-bin/strflog.py /Library/WebServer/CGI-Executables/strflog.cgi
sudo cp -v cgi_ui/strflog_Template.htm /Library/WebServer/Documents/