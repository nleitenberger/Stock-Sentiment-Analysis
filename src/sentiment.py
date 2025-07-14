import nltk, pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer

# Download Lexicon

try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon")
    
sia = SentimentIntensityAnalyzer()

def vader_score(text: str) -> float:
    """Compound Score [-1,1]"""
    return sia.polarity_scores(text)["compound"]

def main() -> None:
    df = pd.read_csv("data/news_raw.csv")
    df["sentiment_vader"] = df["title"].apply(vader_score)
    df.to_csv("data/news_scored.csv", index=False)
    print("VADER Scoring Complete -> data/news_scored.csv")
    

if __name__ == "__main__":
    main()