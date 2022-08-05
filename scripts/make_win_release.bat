
REM execute me from the main directory

rmdir /S dist /Q
rmdir /S build /Q

CALL venv\Scripts\activate.bat

git restore *
git switch master
git pull

venv\Scripts\python.exe -m pip install pip -U
venv\Scripts\pip install -r requirements.txt -U
venv\Scripts\pip install pyinstaller -U
venv\Scripts\pip install -U pyinstaller-hooks-contrib

CALL venv\Scripts\python.exe scripts\make_win_release.py

git restore *