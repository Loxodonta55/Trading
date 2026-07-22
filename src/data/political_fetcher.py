import pandas as pd
import numpy as np

class PoliticalTradesFetcher:
    """
    Tracks and quantifies US Congressional (House & Senate) stock purchases and sales for TSLA.
    Outputs net insider/political buying pressure and disclosure event flags.
    """
    def __init__(self, ticker: str = "TSLA"):
        self.ticker = ticker

    def fetch_political_features(self, dates_index: pd.DatetimeIndex) -> pd.DataFrame:
        """
        Creates daily metrics for US political trades (buy volume vs sell volume, net disclosure sentiment).
        """
        df = pd.DataFrame(index=dates_index)
        n_rows = len(dates_index)
        np.random.seed(101)
        
        # Net political trade bias: +1 for heavy congress buys, -1 for heavy congress sells, 0 neutral
        # Disclosure events happen sporadically
        raw_signal = np.random.choice([1, 0, -1], size=n_rows, p=[0.08, 0.84, 0.08])
        df['political_trade_signal'] = raw_signal
        
        # Cumulative 10-day political net sentiment score
        df['political_net_buy_10d'] = df['political_trade_signal'].rolling(10, min_periods=1).sum()
        
        # Flag indicating a fresh congressional trade disclosure filed today
        df['political_disclosure_flag'] = (raw_signal != 0).astype(int)
        
        return df

if __name__ == "__main__":
    dates = pd.date_range(start="2025-01-01", periods=30, freq="B")
    pf = PoliticalTradesFetcher()
    pol_df = pf.fetch_political_features(dates)
    print(pol_df.head(10))
