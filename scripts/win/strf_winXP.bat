@ECHO OFF

TITLE "Structurefinder - XP version"

rem SET args=%*

SET ppath="Python3.4_32-XP"
rem cls

SET PYTHONPATH=%PYTHONPATH%;.\%ppath%\Lib\site-packages


start .\%ppath%\pythonw.exe strf.py 
