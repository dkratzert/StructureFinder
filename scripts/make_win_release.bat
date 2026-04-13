@echo on

REM execute me from the main directory

REM Python version must match the one in scripts\_create_dist.bat
set PYTHON_VERSION=3.14

rmdir /S dist /Q
rmdir /S build /Q

rem git restore *
rem git switch master
rem git pull

REM Ensure uv is installed
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo uv is not installed. Installing uv...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
)

CALL uv venv --python %PYTHON_VERSION% .venv
CALL .venv\Scripts\activate.bat
CALL uv pip install hatchling

CALL scripts\_create_dist.bat

rem CALL pip install qtpy

CALL .venv\Scripts\python.exe scripts\_make_win_release.py

CALL .venv\Scripts\deactivate.bat
