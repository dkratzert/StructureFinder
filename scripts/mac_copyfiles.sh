#!/bin/bash

sudo cp -r ../searcher/*.py /Library/WebServer/CGI-Executables/searcher/
sudo cp -v ../cgi_ui/cgi-bin/strf_web.py /Library/WebServer/CGI-Executables/strf_web.cgi
sudo cp -v ../cgi_ui/strf_web_Template.htm /Library/WebServer/CGI-Executables/
sudo cp -v ../structuredb.sqlite /Library/WebServer/CGI-Executables/
sudo cp -v ../cgi_ui/cgi-bin/favicon.ico /Library/WebServer/Documents/favicon.ico
sudo cp -v ../displaymol/*.py /Library/WebServer/CGI-Executables/displaymol
sudo cp -v ../displaymol/JSmol_dk.nojq.lite.js /Library/WebServer/Documents/jsmol/