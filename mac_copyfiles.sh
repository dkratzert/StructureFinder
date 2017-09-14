#!/bin/bash

sudo cp -r searcher/database_handler.py /Library/WebServer/CGI-Executables/searcher/
sudo cp -v cgi_ui/cgi-bin/strf_web.py /Library/WebServer/CGI-Executables/strf_web.cgi
sudo cp -v cgi_ui/strf_web_Template.htm /Library/WebServer/CGI-Executables/
sudo cp -v structuredb.sqlite /Library/WebServer/CGI-Executables/