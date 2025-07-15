import nltk, pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
import csv

# Download Lexicon

try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon")
    
sia = SentimentIntensityAnalyzer()

def vader_score(text: str) -> float:
    """Compound Score [-1,1]"""
    return sia.polarity_scores(text)["compound"]

# Label of Vader Results

def vader_label (compound: float) -> str: 
    # Positive
    if compound >= 0.05: 
        return "positive"
    if compound <= -0.05:
        return "negative"
    return "neutral"

def main() -> None:
    df = pd.read_csv("data/news_raw.csv")
    df["sentiment_vader"] = df["title"].apply(vader_score)
    df.to_csv("data/news_scored.csv", index=False)
    
    # Organize .CSV File for Readability
    
    input_path = "data/news_scored.csv"
    output_path = "data/news_scored_grouped.csv"
    
    df_sorted = (
        pd.read_csv(input_path, parse_dates=["published"])
        .sort_values(["ticker", "published"])
    )
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = None
        current_ticker = None
        
        for _, row in df_sorted.iterrows():
            if row ["ticker"] != current_ticker:
                
                # Implement New Ticker Block / Blank Line for Separation
                
                if current_ticker is not None:
                    f.write("\n")
                    
                current_ticker = row ["ticker"]
                
                if writer is None: 
                    writer = csv.DictWriter(f, fieldnames = row.index)
                    writer.writeheader()
                    
                writer.writerow(row.to_dict())
    
    
    print("VADER Scoring Complete -> data/news_scored.csv")
    

if __name__ == "__main__":
    main()