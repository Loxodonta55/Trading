import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from config import PRIMARY_TICKER, BENCHMARK_TICKERS, START_DATE, DATA_DIR

class MarketDataFetcher:
    def __init__(self, ticker: str = PRIMARY_TICKER, start_date: str = START_DATE):
        self.ticker = ticker
        self.start_date = start_date

    def fetch_primary_data(self) -> pd.DataFrame:
        """Fetch daily candle data for the primary stock (e.g. TSLA)."""
        cache_path = DATA_DIR / f"{self.ticker}_daily.csv"
        print(f"[MarketDataFetcher] Fetching {self.ticker} data from {self.start_date}...")
        
        try:
            df = yf.download(self.ticker, start=self.start_date, progress=False)
            if df.empty:
                raise ValueError(f"No data returned for {self.ticker}")
            
            # Flatten multi-index columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            df.reset_index(inplace=True)
            df.rename(columns={'Date': 'date', 'Open': 'open', 'High': 'high', 
                              'Low': 'low', 'Close': 'close', 'Adj Close': 'adj_close', 
                              'Volume': 'volume'}, inplace=True)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # Save to cache
            df.to_csv(cache_path)
            return df
        except Exception as e:
            print(f"[MarketDataFetcher] Warning: Failed to download live data: {e}")
            if cache_path.exists():
                print(f"[MarketDataFetcher] Loading cached data from {cache_path}...")
                df = pd.read_csv(cache_path, index_col='date', parse_dates=True)
                return df
            else:
                raise e

    def fetch_benchmark_data(self) -> pd.DataFrame:
        """Fetch benchmark market indices (SPY, QQQ, VIX) to extract macro market signals."""
        benchmarks = {}
        for b_ticker in BENCHMARK_TICKERS:
            clean_name = b_ticker.replace("^", "").lower()
            try:
                b_df = yf.download(b_ticker, start=START_DATE, progress=False)
                if isinstance(b_df.columns, pd.MultiIndex):
                    b_df.columns = b_df.columns.get_level_values(0)
                b_df.reset_index(inplace=True)
                b_df.rename(columns={'Date': 'date', 'Close': f'{clean_name}_close', 'Volume': f'{clean_name}_volume'}, inplace=True)
                b_df['date'] = pd.to_datetime(b_df['date'])
                b_df.set_index('date', inplace=True)
                benchmarks[clean_name] = b_df[[f'{clean_name}_close']]
            except Exception as e:
                print(f"[MarketDataFetcher] Could not download benchmark {b_ticker}: {e}")
        
        if benchmarks:
            merged_benchmarks = pd.concat(benchmarks.values(), axis=1)
            return merged_benchmarks
        return pd.DataFrame()

if __name__ == "__main__":
    fetcher = MarketDataFetcher()
    tsla_df = fetcher.fetch_primary_data()
    print(f"TSLA Data Shape: {tsla_df.shape}")
    print(tsla_df.head())
