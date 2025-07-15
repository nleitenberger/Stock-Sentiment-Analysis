@echo off
REM ---
REM run.bat - Activate Virtual Environment & Start Streamlit
REM ---

setlocal EnableDelayedExpansion
cd /d "%~dp0"

:: Ensure Virtual Environment Existent
if not exist ".venv" (
    echo [ERROR] Missing .venv - Run Install.bat First.
    pause & exit /b 1
)

:: Activate Virtual Environment
call .venv\Scripts\activate

echo [+] Launching Streamlit on http://localhost...
streamlit run src\app.py --server.headless true