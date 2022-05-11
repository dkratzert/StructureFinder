@ECHO OFF

REM Runs the StructureFinder desktop application

REM Before running this script, you probably need to run this one time,
REM in order to install e virtual environment (venv):
REM
REM python3.9 -m venv venv
REM venv\scripts\activate.bat
REM venv\bin\python3.9 -m pip install pip -U
REM venv\bin\pip3 install -r requirements-cmd.txt
REM


TITLE "Structurefinder"

CALL venv\Scripts\activate.bat
set PYTHONPATH=.

venv\Scripts\python.exe structurefinder/strf.py

