@echo on

REM execute me from the main directory

rmdir /S dist /Q
rmdir /S build /Q

rem git restore *
rem git switch master
rem git pull

CALL scripts\create_dist.bat

CALL venv\Scripts\activate.bat

rem venv\Scripts\python.exe -m pip install pip -U
rem venv\Scripts\pip install -r requirements.txt -U
rem venv\Scripts\pip install pyinstaller -U
rem venv\Scripts\pip install -U pyinstaller-hooks-contrib

CALL venv\Scripts\python.exe scripts\make_win_release.py

CALL venv\Scripts\deactivate.bat
