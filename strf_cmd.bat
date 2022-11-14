@ECHO OFF

REM Runs the StructureFinder commandline indexer in Windows

REM Before running this script, you probably need to run 'install_min_requirements.bat'

TITLE "Structurefinder"

CALL venv\Scripts\activate.bat
set PYTHONPATH=.

venv\Scripts\python.exe src\structurefinder/strf_cmd.py %*

