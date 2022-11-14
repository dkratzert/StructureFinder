@ECHO OFF

REM Runs the StructureFinder desktop application

REM Before running this script, you probably need to run 'install_all_requirements.bat'


TITLE "Structurefinder"

CALL venv\Scripts\activate.bat
set PYTHONPATH=.

venv\Scripts\python.exe src\structurefinder/strf.py %*

