@echo off
REM --
REM install.bat - assuming conda present
REM --
set "ENV_NAME=stock_sentiment"

call conda env list | findstr /C: "%ENV_NAME%" >nul
if %errorlevel% neq 0 (
    echo [+] Creating Conda Environment %ENV_NAME% ...
    conda create -n %ENV_NAME% python=3.12 -y
)

call conda activate %ENV_NAME%
echo [+] Installing Requirements ...
pip install -r requirements.txt --quiet

echo [+] Downloading VADER ...
python - <<PY 2>nul
import nltk, os
nltk.download("vader_lexicon", quiet=True)
PY

echo [+] Setup Complete. Use Run.bat
pause
