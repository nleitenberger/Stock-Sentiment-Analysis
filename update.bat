@echo off
REM ---
REM update.bat - Pull Latest Code & Refresh Dependencies
REM ---

setlocal EnableDelayedExpansion
cd /d "%~dp0"

:: Ensure Git on PATH
where git >NUL 2>&1 || (
    echo [ERROR] Git is not installed or not on PATH.
    pause & exit /b 1
)

:: Pull Latest Commits (Main Branch)
echo [+] Pulling latest commits from origin/main ...
git pull origin main || (
    echo [ERROR] Git pull failed - Resolve Merge Conflicts First
    pause & exit /b 1
)

:: Ensure Python & Virtual Environment
where python >NUL 2>&1 || (
    echo [ERROR] Python Missing - Install Python 3.12
    pause & exit /b 1
)

if not exist ".venv\" (
    echo [+] Creating Virtual Environment .venv ...
    python -m venv .venv
)

:: Activate Virtual Environment
call .venv\Scripts\activate

:: Upgrade PIP & Install/Upgrade Packages 
echo [+] Upgrading pip and dependencies ...
python -m pip install --upgrade pip >NUL
pip install -r requirements.txt --quiet

:: Guarantee VADER Lexicon Existence
python - <<PY 2>NUL
import nltk, os
nltk.download("vader_lexicon", quiet=True)
PY

echo [+] Update Complete. Run "run.bat" to launch. 
pause