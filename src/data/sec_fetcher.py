import requests
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from config import DATA_DIR, PRIMARY_TICKER

# CIK Mapping for Tickers (TSLA CIK: 0001318605)
CIK_MAP = {
    "TSLA": "0001318605"
}

class SecFetcher:
    """
    Ingests official US SEC EDGAR submission filings (Form 8-K, 10-K, 10-Q, Form 4)
    and extracts corporate governance, insider disclosure, and material event signals.
    """
    def __init__(self, ticker: str = PRIMARY_TICKER):
        self.ticker = ticker
        self.cik = CIK_MAP.get(ticker, "0001318605")
        self.cache_path = DATA_DIR / f"{self.ticker}_sec_filings.csv"

    def fetch_sec_filings(self) -> pd.DataFrame:
        """
        Fetches recent official SEC submissions for ticker via SEC EDGAR REST API.
        Caches results locally to optimize speed and API rate limits.
        """
        print(f"[SecFetcher] Ingesting SEC EDGAR filings for {self.ticker} (CIK: {self.cik})...")
        url = f"https://data.sec.gov/submissions/CIK{self.cik}.json"
        headers = {'User-Agent': 'TradingBot boris@example.com'}

        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200:
                print(f"[SecFetcher] Warning: SEC EDGAR API returned status {r.status_code}")
                return self._load_cache_or_fallback()

            data = r.json()
            recent = data.get('filings', {}).get('recent', {})
            
            forms = recent.get('form', [])
            filing_dates = recent.get('filingDate', [])
            doc_descriptions = recent.get('primaryDocDescription', [])
            
            if not forms or not filing_dates:
                return self._load_cache_or_fallback()

            records = []
            for form, date_str, desc in zip(forms, filing_dates, doc_descriptions):
                form_clean = str(form).upper().strip()
                date_dt = pd.to_datetime(date_str)
                
                is_8k = 1 if '8-K' in form_clean else 0
                is_form4 = 1 if form_clean in ['4', '144'] else 0
                is_report = 1 if any(f in form_clean for f in ['10-K', '10-Q']) else 0
                
                records.append({
                    'date': date_dt,
                    'form': form_clean,
                    'description': str(desc),
                    'is_8k': is_8k,
                    'is_form4': is_form4,
                    'is_report': is_report
                })

            raw_df = pd.DataFrame(records)
            raw_df.to_csv(self.cache_path, index=False)
            
            # Aggregate by date
            daily_sec = raw_df.groupby('date').agg(
                sec_filing_flag=('form', lambda x: 1),
                sec_8k_flag=('is_8k', 'max'),
                sec_form4_insider_flag=('is_form4', 'max'),
                sec_10k_10q_flag=('is_report', 'max')
            )
            print(f"[SecFetcher] Successfully processed {len(raw_df)} SEC filings across {len(daily_sec)} unique dates.")
            return daily_sec

        except Exception as e:
            print(f"[SecFetcher] Could not download live SEC filings: {e}")
            return self._load_cache_or_fallback()

    def _load_cache_or_fallback(self) -> pd.DataFrame:
        if self.cache_path.exists():
            print(f"[SecFetcher] Loading cached SEC data from {self.cache_path}...")
            raw_df = pd.read_csv(self.cache_path)
            raw_df['date'] = pd.to_datetime(raw_df['date'])
            daily_sec = raw_df.groupby('date').agg(
                sec_filing_flag=('form', lambda x: 1),
                sec_8k_flag=('is_8k', 'max'),
                sec_form4_insider_flag=('is_form4', 'max'),
                sec_10k_10q_flag=('is_report', 'max')
            )
            return daily_sec
        return pd.DataFrame()

    def fetch_sec_features(self, dates_index: pd.DatetimeIndex) -> pd.DataFrame:
        """
        Aligns daily SEC features with the given dates_index.
        Calculates time-decay, rolling filing metrics, and event indicators.
        """
        df = pd.DataFrame(index=dates_index)
        sec_daily = self.fetch_sec_filings()
        
        if not sec_daily.empty:
            df = df.join(sec_daily, how='left')

        # Fill NaNs for non-filing days
        df['sec_filing_flag'] = df['sec_filing_flag'].fillna(0).astype(int)
        df['sec_8k_flag'] = df['sec_8k_flag'].fillna(0).astype(int)
        df['sec_form4_insider_flag'] = df['sec_form4_insider_flag'].fillna(0).astype(int)
        df['sec_10k_10q_flag'] = df['sec_10k_10q_flag'].fillna(0).astype(int)

        # 30-day rolling sum of SEC filings
        df['sec_filing_count_30d'] = df['sec_filing_flag'].rolling(30, min_periods=1).sum()
        
        # Days since last SEC submission
        days_since = []
        last_seen = 999
        for val in df['sec_filing_flag']:
            if val == 1:
                last_seen = 0
            else:
                last_seen += 1
            days_since.append(last_seen)
        df['days_since_last_sec_filing'] = days_since

        return df

if __name__ == "__main__":
    dates = pd.date_range(start="2025-01-01", periods=30, freq="B")
    sec_fetcher = SecFetcher()
    sec_df = sec_fetcher.fetch_sec_features(dates)
    print("\nSample SEC Features Output:")
    print(sec_df.head(15))
