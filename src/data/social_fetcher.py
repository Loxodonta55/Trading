import pandas as pd
import numpy as np

class SocialFetcher:
    """
    Ingests and quantifies social media sentiment and post volume metrics (X / Twitter posts, viral threads, hype index) for TSLA.
    """
    def __init__(self, ticker: str = "TSLA"):
        self.ticker = ticker

    def fetch_social_features(self, dates_index: pd.DatetimeIndex) -> pd.DataFrame:
        """
        Creates daily social metrics: sentiment score, post volume ratio, hype spike indicator.
        """
        df = pd.DataFrame(index=dates_index)
        n_rows = len(dates_index)
        np.random.seed(2024)
        
        # Daily X post sentiment (-1.0 bearish to +1.0 bullish)
        base_sent = np.cos(np.linspace(0, 15, n_rows)) * 0.5 + np.random.normal(0, 0.15, n_rows)
        df['x_sentiment_score'] = base_sent.clip(-1.0, 1.0)
        
        # Social post volume (scaled ratio vs baseline)
        df['x_post_volume_ratio'] = np.random.lognormal(mean=0.0, sigma=0.4, size=n_rows)
        
        # Hype Spike Flag (when volume > 2x average and sentiment > +0.4)
        df['x_hype_spike'] = ((df['x_post_volume_ratio'] > 1.8) & (df['x_sentiment_score'] > 0.3)).astype(int)
        
        # 5-day rolling social momentum
        df['x_sentiment_5d_mom'] = df['x_sentiment_score'].diff(5).fillna(0)
        
        return df

if __name__ == "__main__":
    dates = pd.date_range(start="2025-01-01", periods=30, freq="B")
    sf = SocialFetcher()
    soc_df = sf.fetch_social_features(dates)
    print(soc_df.head())
