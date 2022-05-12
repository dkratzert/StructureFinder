
REM execute me from the main directory

rmdir /S dist /Q

CALL venv\Scripts\activate.bat

venv\Scripts\pip install pip -U
venv\Scripts\pip install -r requirements.txt
venv\Scripts\pip install pyinstaller

CALL venv\Scripts\python.exe scripts\make_win_release.py

git restore *