@ECHO OFF

TITLE "Structurefinder - XP version"

SET args=%*

cls
start .\pythonw.exe -S stdb.py %args%;exit
