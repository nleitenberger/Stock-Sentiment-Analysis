import os, datetime as dt, pandas as pd
from dotenv import load_dotenv
from newsapi import NewsApiClient

load_dotenv()
API_KEY = os.getenv("NEWSAPI_KEY")
if not API_KEY:
    raise RuntimeError("NEWSAPI_KEY Missing from .env File")

newsapi = NewsApiClient(api_key=API_KEY)

def fetch_company_news(ticker: str, days_back: int = 30) -> pd.DataFrame:
    """Return a DataFrame of Past N Days of Headlines for 'ticker'."""
    start = (dt.date.today() - dt.timedelta(days=days_back)).isoformat()
    out = newsapi.get_everything(
        q=ticker,
        language="en",
        sort_by="publishedAt",
        from_param=start,
        page_size=100,
    )
    
    rows = [
        {
            "ticker": ticker.upper(),
            "published": a["publishedAt"],
            "title": a["title"] or "",
            "source": a["source"]["name"],
            "url": a["url"],
        }
        for a in out["articles"]
    ]
    return pd.DataFrame(rows)

def main() -> None:
    tickers = ["AAPL", "MSFT", "NVDA"]
    frames = [fetch_company_news(t) for t in tickers]
    df = pd.concat(frames, ignore_index=True)
    df.to_csv("data/news_raw.csv", index=False)
    print(f"Saved {len(df):,} rows -> data/news.csv")
    
if __name__ == "__main__":
    main()