@echo off
REM --
REM install.bat - setup & pip
REM --
setlocal EnableDelayedExpansion
cd /d "%~dp0"

:: Verify Python 3.12+ on PATH

where python >NUL 2>&1 || (
    echo [ERROR] Python is not on PATH. Install Python 3.12
    pause & exit /b 1
)

:: Create Virtual Environment if Missing
if not exist ".venv\" (
    echo [+] Creating Virtual Environment .venv...
    python -m venv .venv
)

:: Activate Virtual Environment
call .venv\Scripts\activate

:: Upgrade Pip & Install Dependencies
python - <<PY 2>NUL
import nltk, os
nltk.download("vader_lexicon", quiet=True)
PY

echo[+] Setup Complete. Run "Run.bat" File to Launch.
pause
exit /b 0

:pipfail
echo [ERROR] pip install failed - scroll up for details. 
pause
exit /b 1
