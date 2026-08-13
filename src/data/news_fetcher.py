import logging
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

import json
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from config import FINNHUB_API_KEY

logger = logging.getLogger(__name__)

# Financial Sentiment Lexicons (Loughran-McDonald & VADER financial adaptations)
POSITIVE_WORDS = {
    'surge', 'surged', 'surges', 'rally', 'rallies', 'rallied', 'beat', 'beats', 'beating',
    'growth', 'grew', 'record', 'profit', 'profitable', 'profits', 'bullish', 'upgrade',
    'upgraded', 'jump', 'jumps', 'jumped', 'gain', 'gains', 'gained', 'partnership',
    'expansion', 'deliveries', 'delivered', 'breakthrough', 'soar', 'soared', 'soaring',
    'revenue', 'outperform', 'strong', 'higher', 'rise', 'rises', 'rising', 'boost'
}

NEGATIVE_WORDS = {
    'drop', 'drops', 'dropped', 'plunge', 'plunges', 'plunged', 'fall', 'falls', 'fell',
    'falling', 'loss', 'losses', 'miss', 'misses', 'missed', 'lawsuit', 'recall', 'recalls',
    'recalled', 'downgrade', 'downgraded', 'crash', 'crashed', 'delay', 'delays', 'delayed',
    'warning', 'inquiry', 'investigation', 'slump', 'slumps', 'slumped', 'bearish', 'cut',
    'cuts', 'decline', 'declines', 'declined', 'weakness', 'risk', 'risks', 'threat'
}

class NewsFetcher:
    """
    Ingests live financial news via Yahoo Finance API (yfinance),
    quantifies sentiment using financial NLP lexicon scoring, and builds daily news features.
    """
    def __init__(self, ticker: str = "TSLA") -> None:
        self.ticker = ticker

    def analyze_text_sentiment(self, text: str) -> float:
        """Calculates a normalized sentiment score (-1.0 to +1.0) for a news title or summary."""
        if not text:
            return 0.0
        words = re.findall(r'\b[a-z]+\b', text.lower())
        if not words:
            return 0.0
        
        pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
        neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)
        
        total = pos_count + neg_count
        if total == 0:
            return 0.0
        return (pos_count - neg_count) / float(total)

    def fetch_live_news(self) -> pd.DataFrame:
        """Fetches live news headlines from yfinance and computes sentiment scores."""
        logger.info(f"[NewsFetcher] Fetching live news articles for {self.ticker} via yfinance...")
        try:
            ticker_obj = yf.Ticker(self.ticker)
            raw_news = ticker_obj.news
            if not raw_news:
                logger.warning(f"[NewsFetcher] Warning: No live news returned for {self.ticker}.")
                return pd.DataFrame()

            parsed_news = []
            for item in raw_news:
                content = item.get('content', {})
                title = content.get('title', '')
                summary = content.get('summary', '')
                pub_date_str = content.get('pubDate', '')
                
                # Combine title and summary for NLP evaluation
                full_text = f"{title}. {summary}"
                sentiment_score = self.analyze_text_sentiment(full_text)
                
                # Check for major press release catalyst keywords
                is_catalyst = 1 if any(kw in full_text.lower() for kw in ['earnings', 'q1', 'q2', 'q3', 'q4', 'press release', 'sec filing', 'guidance']) else 0
                
                pub_date = pd.to_datetime(pub_date_str) if pub_date_str else pd.Timestamp.now()
                if hasattr(pub_date, 'tz') and pub_date.tz is not None:
                    pub_date = pub_date.tz_localize(None)
                parsed_news.append({
                    'date': pub_date.floor('D'),
                    'title': title,
                    'sentiment': sentiment_score,
                    'is_catalyst': is_catalyst
                })

            news_df = pd.DataFrame(parsed_news)
            if news_df.empty:
                return pd.DataFrame()

            # Group live news by day
            daily_news = news_df.groupby('date').agg(
                news_sentiment=('sentiment', 'mean'),
                news_volume=('title', 'count'),
                press_release_flag=('is_catalyst', 'max')
            )
            logger.info(f"[NewsFetcher] Processed {len(raw_news)} live news headlines across {len(daily_news)} dates.")
            return daily_news
        except Exception as e:
            logger.warning(f"[NewsFetcher] Warning: Could not fetch live yfinance news: {e}")
            return pd.DataFrame()

    def fetch_google_news_rss(self) -> pd.DataFrame:
        """Fetches live news headlines from Google News RSS feed (Free, no API key)."""
        logger.info(f"[NewsFetcher] Fetching live news articles for {self.ticker} via Google News RSS...")
        try:
            query = urllib.parse.quote(f"{self.ticker} stock")
            url = f"https://news.google.com/rss/search?q={query}+when:3d&hl=en-US&gl=US&ceid=US:en"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                xml_data = response.read()
                
            root = ET.fromstring(xml_data)
            parsed_news = []
            
            for item in root.findall('.//item'):
                title_elem = item.find('title')
                title = title_elem.text if title_elem is not None else ''
                date_elem = item.find('pubDate')
                pub_date_str = date_elem.text if date_elem is not None else ''
                
                sentiment_score = self.analyze_text_sentiment(title)
                is_catalyst = 1 if any(kw in title.lower() for kw in ['earnings', 'q1', 'q2', 'q3', 'q4', 'press release', 'sec filing', 'guidance']) else 0
                
                try:
                    pub_date = pd.to_datetime(pub_date_str)
                    if hasattr(pub_date, 'tz') and pub_date.tz is not None:
                        pub_date = pub_date.tz_localize(None)
                except (ValueError, TypeError):
                    pub_date = pd.Timestamp.now()
                    
                parsed_news.append({
                    'date': pub_date.floor('D'),
                    'title': title,
                    'sentiment': sentiment_score,
                    'is_catalyst': is_catalyst
                })
                
            news_df = pd.DataFrame(parsed_news)
            if news_df.empty:
                return pd.DataFrame()
                
            daily_news = news_df.groupby('date').agg(
                news_sentiment=('sentiment', 'mean'),
                news_volume=('title', 'count'),
                press_release_flag=('is_catalyst', 'max')
            )
            logger.info(f"[NewsFetcher] Processed {len(parsed_news)} live Google news headlines across {len(daily_news)} dates.")
            return daily_news
            
        except Exception as e:
            logger.warning(f"[NewsFetcher] Warning: Could not fetch Google News RSS: {e}")
            return pd.DataFrame()

    def fetch_finnhub_news(self) -> pd.DataFrame:
        """Fetches live company news from Finnhub API using FINNHUB_API_KEY."""
        if not FINNHUB_API_KEY:
            return pd.DataFrame()
        logger.info(f"[NewsFetcher] Fetching real-time company news for {self.ticker} via Finnhub API...")
        try:
            today = datetime.now().date()
            from_date = today - pd.Timedelta(days=14)
            url = f"https://finnhub.io/api/v1/company-news?symbol={self.ticker}&from={from_date}&to={today}&token={FINNHUB_API_KEY}"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=8) as response:
                articles = json.loads(response.read().decode('utf-8'))
            
            if not articles:
                return pd.DataFrame()

            parsed_news = []
            for item in articles:
                headline = item.get('headline', '')
                summary = item.get('summary', '')
                datetime_ts = item.get('datetime', 0)
                
                full_text = f"{headline}. {summary}"
                sentiment_score = self.analyze_text_sentiment(full_text)
                is_catalyst = 1 if any(kw in full_text.lower() for kw in ['earnings', 'q1', 'q2', 'q3', 'q4', 'press release', 'sec filing', 'guidance']) else 0
                
                pub_date = pd.to_datetime(datetime_ts, unit='s') if datetime_ts else pd.Timestamp.now()
                parsed_news.append({
                    'date': pub_date.floor('D'),
                    'title': headline,
                    'sentiment': sentiment_score,
                    'is_catalyst': is_catalyst
                })
            
            news_df = pd.DataFrame(parsed_news)
            if news_df.empty:
                return pd.DataFrame()
            
            daily_news = news_df.groupby('date').agg(
                news_sentiment=('sentiment', 'mean'),
                news_volume=('title', 'count'),
                press_release_flag=('is_catalyst', 'max')
            )
            logger.info(f"[NewsFetcher] Finnhub API: Processed {len(articles)} live articles across {len(daily_news)} dates.")
            return daily_news
        except Exception as e:
            logger.warning(f"[NewsFetcher] Finnhub API fetch failed: {e}")
            return pd.DataFrame()

    def fetch_news_features(self, dates_index: pd.DatetimeIndex) -> pd.DataFrame:
        """
        Builds aligned daily news features for dates in dates_index.
        Merges live Finnhub API, yfinance news feeds and Google News with historical sentiment signals.
        """
        df = pd.DataFrame(index=dates_index)
        
        # 1. Fetch Live News across available sources (Finnhub API first, then yfinance & Google News)
        finnhub_news_df = self.fetch_finnhub_news()
        live_news_df = self.fetch_live_news()
        google_news_df = self.fetch_google_news_rss()
        
        all_news_dfs = [df_item for df_item in [finnhub_news_df, live_news_df, google_news_df] if not df_item.empty]
        combined_live = pd.DataFrame()
        if all_news_dfs:
            combined = pd.concat(all_news_dfs)
            combined_live = combined.groupby(combined.index).agg({
                'news_sentiment': 'mean',
                'news_volume': 'sum',
                'press_release_flag': 'max'
            })
        
        # 2. Base historical sentiment signal
        # WARNING: Synthetic historical baseline — replace with real data source
        logger.warning("[NewsFetcher] Generating synthetic historical sentiment signals. Replace with real data source.")
        np.random.seed(42)
        n_rows = len(dates_index)
        hist_sentiment = np.sin(np.linspace(0, 10, n_rows)) * 0.4 + np.random.normal(0, 0.15, n_rows)
        hist_sentiment = np.clip(hist_sentiment, -1.0, 1.0)
        
        df['news_sentiment'] = hist_sentiment
        df['press_release_flag'] = (np.random.rand(n_rows) > 0.85).astype(int)
        df['news_volume'] = np.random.poisson(lam=12, size=n_rows)

        # 3. Merge Live News Data where available
        if not combined_live.empty:
            for d in combined_live.index:
                # Remove timezone if needed to match index
                d_clean = d.tz_localize(None) if d.tz is not None else d
                if d_clean in df.index:
                    df.loc[d_clean, 'news_sentiment'] = combined_live.loc[d, 'news_sentiment']
                    df.loc[d_clean, 'news_volume'] = combined_live.loc[d, 'news_volume']
                    df.loc[d_clean, 'press_release_flag'] = combined_live.loc[d, 'press_release_flag']

        # 4. Compute 3-day rolling average sentiment
        df['news_sentiment_3d_ma'] = df['news_sentiment'].rolling(3, min_periods=1).mean()
        
        return df

if __name__ == "__main__":
    dates = pd.date_range(start="2025-01-01", periods=30, freq="B")
    nf = NewsFetcher()
    news_df = nf.fetch_news_features(dates)
    logger.info("\nSample Output with Live yfinance News Integration:")
    logger.info(f"\n{news_df.tail(10)}")
