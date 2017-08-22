@ECHO OFF

TITLE "Structurefinder"
SET mypath=%~dp0
SET mydrive = %~d0

%~d0

cd %~dp0

start .\Python3.6.1-32\pythonw.exe "%mypath%strf.py" %1
rem pause
exit
