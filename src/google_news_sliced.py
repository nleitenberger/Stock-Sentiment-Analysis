from __future__ import annotations

import datetime as dt 
import time
import urllib.parse as qp
import feedparser
import pandas as pd 

BASE = (
    "https://news.google.com/rss/search?"
    "q={query}&hl=en-US&gl=US&ceid=US:en"
)

def _window_url(ticker: str, start: dt.date, end: dt.date) -> str:
    query = f'"{ticker} stock" after:{start} before:{end}'
    return BASE.format(query=qp.quote_plus(query))
    
def fetch_google_news_sliced(ticker: str, days_back: int = 30, slice_len: int = 7) -> pd.DataFrame:
    today = dt.date.today()
    start = today - dt.timedelta(days=days_back)
    frames = []
    cur_end = today
    
    ticker_up = ticker.upper()
    
    while cur_end > start:
        cur_start = max(start, cur_end - dt.timedelta(days=slice_len))
        feed = feedparser.parse(_window_url(ticker_up, cur_start, cur_end))
        rows = []
        for e in feed.entries:
            ts = dt.datetime(*e.published_parsed[:6])
            if ts.date() < start:
                continue
            rows.append({
                "ticker": ticker_up,
                "published": ts.isoformat(),
                "title": e.title,
                "source": e.source.title if "source" in e else "Google News",
                "url": e.link,
            })
        frames.append(pd.DataFrame(rows))
        cur_end = cur_start
        time.sleep(0.5)
        
    df = (pd.concat(frames, ignore_index=True) .drop_duplicates("url"))
    
    return df[["ticker", "published", "title", "source", "url"]]