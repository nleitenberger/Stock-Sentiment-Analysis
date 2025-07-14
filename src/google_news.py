from __future__ import annotations

import time
import urllib.parse as urlparse
import datetime as dt 

import pandas as pd 
import requests
import feedparser
import bs4

HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )
}

BASE_RSS = (
    "https://news.google.com/rss/search?"
    "q={query}"
    "&hl=en-US&gl=US&ceid=US:en"
)

def _rss_url(ticker: str) -> str:
    # Google News RSS URL for <TICKER>
    query = urlparse.quote_plus(f"{ticker} stock")
    return BASE_RSS.format(query=query)

def _utc_iso(ts_struct) -> str:
    return dt.datetime(*ts_struct[:6]).isoformat()

def fetch_google_news(ticker: str, days_back: int = 30) -> pd.DataFrame:
    
    #FYI - Google News Only Permits 100 Items per Query 
    
    rss_url = _rss_url(ticker)
    feed = feedparser.parse(rss_url)
    
    if feed.bozo:
        # Bozo Flag (Parsing Failure)
        
        print(f"[WARNING] Google News Parse Error for {ticker}: {feed.bozo_exception}")
        return pd.DataFrame(columns=["ticker", "published", "title", "source", "url"])
    
    cutoff = dt.datetime.utcnow() - dt.timedelta(days = days_back)
    records: list[dict[str, str]] = []
    
    for entry in feed.entries:
        ts = dt.datetime(*entry.published_parsed[:6])
        
        if ts < cutoff:
            break
    
        source = entry.source.title if "source" in entry else "Google News"
        records.append({
            "ticker": ticker.upper(),
            "published": ts.isoformat(),
            "title": entry.title,
            "source": source,
            "url": entry.link,
            }
        )   
        
        time.sleep(0.5)
        return pd.DataFrame(records)
    

def fetch_gnews_with_snippet(ticker: str, days_back=30) -> pd.DataFrame:
    url = _rss_url(ticker)
    feed = feedparser.parse(url)
    cutoff = dt.datetime.utcnow() - dt.timedelta(days=days_back)
    
    rows = list[dict[str, str]] = []
    for e in feed.entries:
        ts = dt.datetime(*e.published_parsed[:6])
        if ts < cutoff:
            break
        
        snippet = ""
        try:
            html = requests.get(e.link, headers=HEADERS, timeout=10).text
            soup = bs4.BeautifulSoup(html, "lxml")
            first_p = soup.select_one("p")
            snippet = first_p.text.strip() if first_p else ""
        except Exception:
            pass
        
        rows.append({
            "ticker": ticker.upper(),
            "published": ts.isoformat(),
            "title": e.title,
            "source": e.source.title if "source" in e else "Google News",
            "url": e.link,
            "snippet": snippet,
        })
        time.sleep(0.5) 
        
    return pd.DataFrame(rows)

    
if __name__ == "__main__":
    import sys
    
    sym = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    days = int(sys.argv[2]) if len (sys.argv) > 2 else 7
    
    df_test = fetch_google_news(sym, days_back=days)
    print(f"Rows Scraped for {sym}: {len(df_test)}")
    print(df_test.head())