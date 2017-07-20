@ECHO OFF

TITLE "Structurefinder - XP version"

rem SET args=%*

rem cls

SET PYTHONPATH=%PYTHONPATH%;.\Python3.4_32\Lib\site-packages


start .\Python3.4_32\pythonw.exe stdb.py
