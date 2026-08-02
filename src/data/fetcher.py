import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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
        """
        Fetch daily candle data for the target stock (e.g. TSLA, GOOGL, SPCX).
        Implements INCREMENTAL DELTA FETCHING:
        - If cache/DB exists, reads the last recorded date (T_last).
        - Downloads ONLY the delta range (T_last + 1 day to Today).
        - Merges delta with existing history to eliminate redundant API calls.
        """
        cache_path = DATA_DIR / f"{self.ticker}_daily.csv"
        
        cached_df = None
        if cache_path.exists():
            try:
                cached_df = pd.read_csv(cache_path, index_col='date', parse_dates=True)
                if not cached_df.empty:
                    last_date = cached_df.index.max()
                    print(f"[MarketDataFetcher] Found existing dataset for {self.ticker} up to {last_date.strftime('%Y-%m-%d')}.")
            except Exception as e:
                print(f"[MarketDataFetcher] Warning reading cache for {self.ticker}: {e}")
                cached_df = None

        if cached_df is not None and not cached_df.empty:
            last_date = cached_df.index.max()
            delta_start = last_date + pd.Timedelta(days=1)
            today_date = datetime.now().date()
            today_str = datetime.now().strftime('%Y-%m-%d')
            delta_start_str = delta_start.strftime('%Y-%m-%d')

            if delta_start.date() <= today_date:
                print(f"[MarketDataFetcher] [DELTA UPDATE] Fetching ONLY new data for {self.ticker} from {delta_start_str} to {today_str}...")
                try:
                    delta_df = yf.download(self.ticker, start=delta_start_str, progress=False)
                    if not delta_df.empty:
                        if isinstance(delta_df.columns, pd.MultiIndex):
                            delta_df.columns = delta_df.columns.get_level_values(0)
                        
                        delta_df.reset_index(inplace=True)
                        if 'Date' in delta_df.columns:
                            delta_df.rename(columns={'Date': 'date'}, inplace=True)
                        elif 'index' in delta_df.columns:
                            delta_df.rename(columns={'index': 'date'}, inplace=True)
                        
                        delta_df.rename(columns={'Open': 'open', 'High': 'high', 
                                                 'Low': 'low', 'Close': 'close', 'Adj Close': 'adj_close', 
                                                 'Volume': 'volume'}, inplace=True)
                        delta_df['date'] = pd.to_datetime(delta_df['date'])
                        delta_df.set_index('date', inplace=True)

                        # Merge existing cached history and new delta
                        merged_df = pd.concat([cached_df, delta_df])
                        merged_df = merged_df[~merged_df.index.duplicated(keep='last')]
                        merged_df.sort_index(inplace=True)

                        merged_df.to_csv(cache_path)
                        print(f"[MarketDataFetcher] [SUCCESS] Delta update complete: Added {len(delta_df)} new candles for {self.ticker}. Total: {len(merged_df)} rows.")
                        return merged_df
                    else:
                        print(f"[MarketDataFetcher] [INFO] No new trading sessions since {last_date.strftime('%Y-%m-%d')}. Using existing dataset.")
                        return cached_df
                except Exception as e:
                    print(f"[MarketDataFetcher] Warning: Delta download failed ({e}). Falling back to existing cached dataset.")
                    return cached_df
            else:
                print(f"[MarketDataFetcher] [INFO] Dataset for {self.ticker} is fully up to date ({last_date.strftime('%Y-%m-%d')}).")
                return cached_df

        # Initial full download if no cache exists
        print(f"[MarketDataFetcher] [INITIAL] Downloading full dataset for {self.ticker} from {self.start_date}...")
        try:
            df = yf.download(self.ticker, start=self.start_date, progress=False)
            if df.empty:
                raise ValueError(f"No data returned for {self.ticker}")
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            df.reset_index(inplace=True)
            if 'Date' in df.columns:
                df.rename(columns={'Date': 'date'}, inplace=True)
            elif 'index' in df.columns:
                df.rename(columns={'index': 'date'}, inplace=True)

            df.rename(columns={'Open': 'open', 'High': 'high', 
                              'Low': 'low', 'Close': 'close', 'Adj Close': 'adj_close', 
                              'Volume': 'volume'}, inplace=True)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            df.to_csv(cache_path)
            print(f"[MarketDataFetcher] [SUCCESS] Full initial download complete for {self.ticker} ({len(df)} rows).")
            return df
        except Exception as e:
            print(f"[MarketDataFetcher] Error initializing data for {self.ticker}: {e}")
            if cache_path.exists():
                return pd.read_csv(cache_path, index_col='date', parse_dates=True)
            raise e

    def fetch_benchmark_data(self) -> pd.DataFrame:
        """
        Fetch benchmark market indices (SPY, QQQ, VIX) with incremental delta caching.
        """
        cache_path = DATA_DIR / "benchmarks_daily.csv"
        cached_df = None

        if cache_path.exists():
            try:
                cached_df = pd.read_csv(cache_path, index_col='date', parse_dates=True)
            except Exception:
                cached_df = None

        benchmarks = {}
        need_full = cached_df is None or cached_df.empty
        today_date = datetime.now().date()

        for b_ticker in BENCHMARK_TICKERS:
            clean_name = b_ticker.replace("^", "").lower()
            try:
                if not need_full:
                    last_date = cached_df.index.max()
                    delta_start = last_date + pd.Timedelta(days=1)
                    if delta_start.date() <= today_date:
                        delta_start_str = delta_start.strftime('%Y-%m-%d')
                        b_df = yf.download(b_ticker, start=delta_start_str, progress=False)
                    else:
                        b_df = pd.DataFrame()
                else:
                    b_df = yf.download(b_ticker, start=START_DATE, progress=False)

                if not b_df.empty:
                    if isinstance(b_df.columns, pd.MultiIndex):
                        b_df.columns = b_df.columns.get_level_values(0)
                    b_df.reset_index(inplace=True)
                    if 'Date' in b_df.columns:
                        b_df.rename(columns={'Date': 'date'}, inplace=True)
                    elif 'index' in b_df.columns:
                        b_df.rename(columns={'index': 'date'}, inplace=True)

                    if 'Close' in b_df.columns:
                        b_df.rename(columns={'Close': f'{clean_name}_close'}, inplace=True)
                    
                    b_df['date'] = pd.to_datetime(b_df['date'])
                    b_df.set_index('date', inplace=True)
                    if f'{clean_name}_close' in b_df.columns:
                        benchmarks[clean_name] = b_df[[f'{clean_name}_close']]
            except Exception as e:
                print(f"[MarketDataFetcher] Benchmark delta fetch warning ({b_ticker}): {e}")

        if benchmarks:
            new_benchmarks = pd.concat(benchmarks.values(), axis=1)
            if cached_df is not None and not cached_df.empty:
                merged = pd.concat([cached_df, new_benchmarks])
                merged = merged[~merged.index.duplicated(keep='last')].sort_index()
                merged.to_csv(cache_path)
                return merged
            else:
                new_benchmarks.to_csv(cache_path)
                return new_benchmarks
        elif cached_df is not None:
            return cached_df

        return pd.DataFrame()

if __name__ == "__main__":
    fetcher = MarketDataFetcher()
    tsla_df = fetcher.fetch_primary_data()
    print(f"TSLA Data Shape: {tsla_df.shape}")
    print(tsla_df.tail())
