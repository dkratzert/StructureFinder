#!/bin/bash

sudo cp -r searcher/database_handler.py /Library/WebServer/CGI-Executables/searcher/
sudo cp -v cgi_ui/cgi-bin/strflog.py /Library/WebServer/CGI-Executables/strflog.cgi
sudo cp -v cgi_ui/strflog_Template.htm /Library/WebServer/CGI-Executables/
sudo cp -v structuredb.sqlite /Library/WebServer/CGI-Executables/