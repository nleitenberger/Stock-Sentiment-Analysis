import streamlit as st
import pandas as pd
import altair as alt
import datetime as dt

from sentiment import vader_score
from newsapi_collect import fetch_company_news

st.set_page_config(page_title="Stock News VADER Sentiment", layout="wide")
st.title("Vader Sentiment on Stock Headlines")

# Sidebar

with st.sidebar:
    st.header("Query")
    tickers = st.text_input("Tickers (comma-separated)", "AAPL,MSFT,NVDA")
    days = st.slider("Days Back", 1, 60, 30)
    run = st.button("Fetch & Analyze")
    
if run:
    symbols = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    if not symbols: 
        st.error("Enter at least one ticker.")
        st.stop()
        
    data_frames = []
    prog = st.progress(0)
    for i, tkr in enumerate(symbols, start=1):
        df_tkr = fetch_company_news(tkr, days_back=days)
        df_tkr["sentiment"] = df_tkr["title"].apply(vader_score)
        data_frames.append(df_tkr)
        prog.progress(i / len(symbols))
    prog.empty()
    
    if not data_frames:
        st.warning("No data returned. Try different parameters!")
        st.stop()
        
    df = pd.concat(data_frames, ignore_index=True)
    df["published"] = pd.to_datetime(df["published"])
    
    st.success(f"{len(df):,} headlines loaded.")
    st.dataframe(df.head(15), use_container_width=True)
    
    # Line Chart for Daily Average
    
    df["date"] = pd.to_datetime(df["published"]).dt.date
    
    daily = (
        df.groupby(["ticker", "date"], as_index=False)
        .sentiment.mean()
        .rename(columns={"sentiment": "avg_sent"})
    )
    
    chart = (
        alt.Chart(daily)
        .mark_line(point=True)
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("avg_sent:Q", title="Average VADER compound"),
            color="ticker:N",
            tooltip=[
                "ticker:N",
                "date:T",
                alt.Tooltip("avg_sent:Q", format=".2f"),
            ],
        )
        .properties(height=400)
    )
    st.altair_chart(chart, use_container_width=True)
    
    # Download Link
    csv = df.to_csv(index=False).encode()
    st.download_button("Download Scored CSV", csv, "news_scored_vader.csv", "text/csv")

else:
    st.info("<-- Enter Tickers & Click 'Fetch & Analyze'.")