import time
import os
import datetime as dt
from datetime import date, timedelta
import pandas as pd
from dotenv import load_dotenv
from newsapi import NewsApiClient

load_dotenv()
API_KEY = os.getenv("NEWSAPI_KEY")
if not API_KEY:
    raise RuntimeError("NEWSAPI_KEY Missing from .env File")

newsapi = NewsApiClient(api_key=API_KEY)

# Attempt to Fetch Slices to Avoid Article Truncation

def fetch_news_sliced(ticker: str, days_back: int = 30, slice_len: int = 3) -> pd.DataFrame:
    end = date.today()
    start = end - timedelta(days=days_back)
    rows = []
    
    slice_to = end
    while slice_to > start:
        slice_from = slice_to - timedelta(days=slice_len)
        if slice_from < start:
            slice_from = start
            
        # For NewsAPI Request
        resp = newsapi.get_everything(
            q = ticker,
            language = "en",
            sort_by = "publishedAt",
            from_param = slice_from.isoformat(),
            to = slice_to.isoformat(),
            page_size = 100,
            page = 1,
        )
        
        for a in resp["articles"]:
            rows.append({
                "ticker": ticker.upper(),
                "published": a["publishedAt"],
                "title": a["title"] or "",
                "source": a["source"]["name"],
                "url": a["url"],
            })
        
        slice_to = slice_from - timedelta(days = 1)
        time.sleep(0.5)
        
    # Deduplicate by URL to prevent duplicate occurrences in slices
    
    df = pd.DataFrame(rows).drop_duplicates(subset="url")
    return df

def main() -> None:
    tickers = ["AAPL", "MSFT", "NVDA"]
    frames = [fetch_company_news(t) for t in tickers]
    df = pd.concat(frames, ignore_index=True)
    df.to_csv("data/news_raw.csv", index=False)
    print(f"Saved {len(df):,} rows -> data/news.csv")
    
if __name__ == "__main__":
    main()