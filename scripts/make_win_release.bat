@echo on

REM execute me from the main directory

rmdir /S dist /Q
rmdir /S build /Q

rem git restore *
rem git switch master
rem git pull

CALL scripts\_create_dist.bat

CALL venv\Scripts\activate.bat
rem CALL pip install qtpy

CALL venv\Scripts\python.exe scripts\_make_win_release.py

CALL venv\Scripts\deactivate.bat
