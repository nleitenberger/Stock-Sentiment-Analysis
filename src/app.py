import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np
import datetime as dt
import io, csv

from sentiment import vader_score
from sentiment import vader_label
from google_news_sliced import fetch_google_news_sliced as fetch_news_sliced

st.set_page_config(page_title="Stock News VADER Sentiment", layout="wide")
st.title("Vader Sentiment on Stock Headlines")

# Sidebar

with st.sidebar:
    st.header("Query")
    tickers = st.text_input("Tickers (comma-separated)", "AAPL,MSFT,NVDA")
    days = st.slider("Days Back", 1, 60, 30)
    drop_neutral = st.checkbox("Exclude Neutral (Sentiment = 0)", value = False)
    run = st.button(" Fetch & Analyze ")
    
if run:
    symbols = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    if not symbols: 
        st.error("Enter at least one ticker.")
        st.stop()
        
    data_frames = []
    prog = st.progress(0)
    for i, tkr in enumerate(symbols, start=1):
        df_tkr = fetch_news_sliced(tkr, days_back=days)
        df_tkr["sentiment"] = df_tkr["title"].apply(vader_score)
        data_frames.append(df_tkr)
        prog.progress(i / len(symbols))
    prog.empty()
    
    if not data_frames:
        st.warning("No data returned. Try different parameters!")
        st.stop()
        
    df = pd.concat(data_frames, ignore_index=True)
    
    # Implementation of Checkbox to Remove Neutral Sentiment Values
    
    if drop_neutral:
        df = df[df["sentiment"] != 0].reset_index(drop=True)
        
    df["published"] = pd.to_datetime(df["published"])
    
    # Vader Labeling
    df["sentiment"] = df["title"].apply(vader_score)
    df["sent_label"] = df["sentiment"].apply(vader_label)
    
    st.success(f"{len(df):,} headlines loaded.")
    st.dataframe(df.head(15), use_container_width=True)
    
    # Updated Chart (Now with Matplotlib.pyplot) for Daily Average
    
    df["date"] = pd.to_datetime(df["published"]).dt.date
    
    daily = (
        df.groupby(["date", "ticker"], as_index=False)["sentiment"]
        .mean()
    )
    
    # Pivot for Matrix
    
    pivot = (
        daily.pivot(index="date", columns="ticker", values="sentiment")
        .sort_index()
        .fillna(0)
    )
    
    st.text(f"DEBUG> After Scraping: {len(df_tkr)} rows")
    df_tkr = df_tkr[df_tkr["sentiment"] != 0]
    st.text(f"DEBUG> After Filter: {len(df_tkr)} rows")
    
    dates = pivot.index
    tickers = pivot.columns
    n_tkr = len(tickers)
    
    if n_tkr == 0:
        st.warning("Nothing to Plot - No Headlines After Filtration.")
        st.stop()
    
    # Grouped Bars
    x = np.arange(len(dates))
    bar_w = 0.8 / n_tkr # Cluster Width --> 0.8
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    for i, tkr in enumerate(tickers):
        offset = (i - (n_tkr - 1) / 2) * bar_w # Centered Clusters
        ax.bar(x + offset, pivot[tkr], width=bar_w, label=tkr)
        
    # Design
    
    ax.axhline(0, color="black", lw=0.7)
    ax.set_ylabel("Average VADER Compound")
    ax.set_xlabel("Date")
    ax.set_title("Daily VADER Sentiment (Grouped Bar Chart)")
    ax.set_xticks(x)
    ax.set_xticklabels([d.strftime("%Y-%m-%d") for d in dates], rotation = 45, ha = "right")
    ax.legend(title="Ticker")
    fig.tight_layout()
    
    # Display via Streamlit
    
    st.pyplot(fig)
    
    
    # -- Download Link --
    
    # Sort by Ticker & Date(s)
    
    df_sorted = df.sort_values(["ticker", "published"])
    df_sorted = df_sorted.rename(columns={
        "sentiment": "compound", 
        "sent_label": "sentiment_class",
    })
    
    # Implement Blank Line into CSV Between Altered Ticker Blocks
    
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(df_sorted.columns)
    
    current = None
    for row in df_sorted.itertuples(index=False): 
        if row.ticker != current and current is not None:
            writer.writerow([])
        writer.writerow(row)
        current = row.ticker
        
    csv_bytes = buffer.getvalue().encode()
    
    suffix = "_no_neutrals" if drop_neutral else ""
    
    st.download_button("Download Grouped CSV", csv_bytes, "news_scored_grouped.csv", "text/csv")

else:
    st.info("<-- Enter Tickers & Click 'Fetch & Analyze'.")