@ECHO OFF

TITLE "Structurefinder - XP version"

SET args=%*

rem cls

SET PYTHONPATH=%PYTHONPATH%;.\Python3.4_32\Lib\site-packages

IF NOT DEFINED DSR_DIR (GOTO setdsrdir) ELSE (GOTO arguments)


:setdsrdir
    SET DSR_DIR="."
    goto arguments

:arguments
    IF DEFINED args (GOTO main) ELSE (GOTO help)    
    goto main

:main
    .\Python3.4_32\python.exe -S stdb.py %args%
    GOTO end

:help
    .\Python3.4_32\python.exe -S stdb.py -h
    GOTO end

:end

PAUSE