@ECHO OFF

TITLE "Structurefinder"

CALL venv\Scripts\activate.bat
set PYTHONPATH=.

start python.exe structurefinder/strf_cmd.py

