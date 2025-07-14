@echo offset "ENV_NAME=stock_sentiment"

call conda activate %ENV_NAME%
if not exist ".env" (
    echo [ERROR] .env with NEWSAPI_KEY missing.
    pause & exit /b 1
)

echo [+] Launching Streamlit on http://localhost...
streamlit run src\app.py --server.headless true