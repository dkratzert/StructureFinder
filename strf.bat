@ECHO OFF

TITLE "Structurefinder"

CALL venv\Scripts\activate.bat
set PYTHONPATH=.

start pythonw.exe structurefinder/strf.py

exit
