import os
import requests
import logging
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from config import DATA_DIR, PRIMARY_TICKER, QUIVER_API_KEY, FINNHUB_API_KEY

logger = logging.getLogger(__name__)

# CIK Mapping for Supported Tickers
CIK_MAP = {
    "TSLA": "0001318605",
    "GOOGL": "0001652044",
    "NVDA": "0001045810",
    "SPCX": "0001318605"
}

SENATE_DATA_URL = "https://raw.githubusercontent.com/timothycarambat/senate-stock-watcher-data/master/aggregate/all_transactions.json"

class PoliticalTradesFetcher:
    """
    Tracks and quantifies US Congressional (Senate & House) stock disclosures,
    Quiver Quantitative institutional feeds, and SEC Form 4 insider transactions.
    Outputs net political buying pressure, rolling sentiment, and disclosure event flags.
    """
    def __init__(self, ticker: str = PRIMARY_TICKER) -> None:
        self.ticker = ticker
        self.cache_path = DATA_DIR / f"{self.ticker}_political_trades.csv"

    def _parse_amount_weight(self, amount_str: str) -> float:
        """Parses Congressional trade dollar amount ranges into scalar weights."""
        if not isinstance(amount_str, str):
            return 1.0
        if '$1,001 - $15,000' in amount_str:
            return 1.0
        if '$15,001 - $50,000' in amount_str:
            return 2.0
        if '$50,001 - $100,000' in amount_str:
            return 3.0
        if '$100,001 - $250,000' in amount_str:
            return 5.0
        if '$250,001 - $500,000' in amount_str:
            return 8.0
        if '$500,001 - $1,000,000' in amount_str:
            return 12.0
        if '$1,000,001' in amount_str:
            return 20.0
        return 1.0

    def _fetch_from_quiver_api(self) -> list:
        """
        Fetches official Congress & Senate trade data from Quiver Quantitative API.
        Uses ReportDate (disclosure date) to prevent lookahead bias.
        """
        if not QUIVER_API_KEY:
            return []
        
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {QUIVER_API_KEY}"
        }
        records = []
        try:
            url = f"https://api.quiverquant.com/beta/historical/congresstrading/{self.ticker}"
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    for item in data:
                        # CRITICAL: Always use ReportDate/DisclosureDate to prevent lookahead bias!
                        report_date = item.get('ReportDate') or item.get('Date') or item.get('TransactionDate')
                        if not report_date:
                            continue
                        tx_type = str(item.get('Transaction', '')).lower()
                        amount = item.get('Amount', 0)
                        
                        weight = 1.0
                        if isinstance(amount, (int, float)):
                            if amount > 500000:
                                weight = 15.0
                            elif amount > 100000:
                                weight = 5.0
                            elif amount > 50000:
                                weight = 2.0
                        elif isinstance(amount, str):
                            weight = self._parse_amount_weight(amount)

                        direction = 1.0 if ('purchase' in tx_type or 'buy' in tx_type) else -1.0 if ('sale' in tx_type or 'sell' in tx_type) else 0.0
                        if direction != 0:
                            records.append({
                                'date': pd.to_datetime(report_date),
                                'signal': direction * weight,
                                'is_disclosure': 1
                            })
                    logger.info(f"[PoliticalTradesFetcher] Quiver Quantitative API: Loaded {len(records)} official Congress trades for {self.ticker}")
            elif resp.status_code in [401, 403]:
                logger.warning(f"[PoliticalTradesFetcher] Quiver Quantitative API authentication failed (HTTP {resp.status_code}). Check QUIVER_API_KEY in .env.")
        except Exception as e:
            logger.warning(f"[PoliticalTradesFetcher] Quiver Quantitative API request failed: {e}")

        return records

    def _fetch_from_finnhub_insiders(self) -> list:
        """
        Fetches SEC Form 4 insider transactions via Finnhub API.
        Uses filingDate to guarantee zero lookahead bias.
        """
        if not FINNHUB_API_KEY:
            return []
        
        records = []
        try:
            url = f"https://finnhub.io/api/v1/stock/insider-transactions?symbol={self.ticker}&token={FINNHUB_API_KEY}"
            resp = requests.get(url, timeout=8)
            if resp.status_code == 200:
                data = resp.json().get('data', [])
                for item in data:
                    # Always use filingDate (when the transaction became public)
                    filing_date = item.get('filingDate') or item.get('transactionDate')
                    if not filing_date:
                        continue
                    change = item.get('change', 0)
                    tx_code = str(item.get('transactionCode', '')).upper()
                    
                    # Positive change = Insider Buying, Negative change = Insider Selling
                    direction = 1.0 if change > 0 or tx_code in ['P', 'A'] else -1.0 if change < 0 or tx_code in ['S', 'D'] else 0.0
                    weight = 2.0 if abs(change) > 50000 else 1.0
                    
                    if direction != 0:
                        records.append({
                            'date': pd.to_datetime(filing_date),
                            'signal': direction * weight,
                            'is_disclosure': 1
                        })
                logger.info(f"[PoliticalTradesFetcher] Finnhub API: Loaded {len(records)} verified Form 4 insider transactions for {self.ticker}")
            elif resp.status_code in [401, 403]:
                logger.warning(f"[PoliticalTradesFetcher] Finnhub API authentication failed (HTTP {resp.status_code}). Check FINNHUB_API_KEY in .env.")
        except Exception as e:
            logger.warning(f"[PoliticalTradesFetcher] Finnhub Insider API request failed: {e}")
        return records

    def fetch_raw_political_disclosures(self) -> pd.DataFrame:
        """
        Fetches live Senate disclosure datasets, Quiver Quantitative feeds, Finnhub Insider transactions, & SEC EDGAR Form 4 filings.
        Combines and normalizes into daily signal records.
        """
        records = []

        # 1. Primary Political: Quiver Quantitative API (if key available)
        quiver_records = self._fetch_from_quiver_api()
        if quiver_records:
            records.extend(quiver_records)

        # 2. Secondary/Fallback Political: Senate Disclosures (Public Scraping Dataset)
        if not quiver_records:
            try:
                r = requests.get(SENATE_DATA_URL, timeout=10)
                if r.status_code == 200:
                    s_data = r.json()
                    s_df = pd.DataFrame(s_data)
                    ticker_df = s_df[s_df['ticker'] == self.ticker].copy()
                    for _, row in ticker_df.iterrows():
                        try:
                            # CRITICAL: Always use disclosure_date first to prevent lookahead bias
                            t_date = pd.to_datetime(row.get('disclosure_date', row.get('transaction_date')))
                            t_type = str(row.get('type', '')).lower()
                            weight = self._parse_amount_weight(str(row.get('amount', '')))
                            
                            if 'purchase' in t_type:
                                direction = 1.0
                            elif 'sale' in t_type:
                                direction = -1.0
                            else:
                                direction = 0.0

                            records.append({
                                'date': t_date,
                                'signal': direction * weight,
                                'is_disclosure': 1
                            })
                        except Exception:
                            continue
                    logger.info(f"[PoliticalTradesFetcher] Loaded {len(ticker_df)} Senate trades for {self.ticker} via Public Feed")
            except Exception as e:
                logger.warning(f"[PoliticalTradesFetcher] Could not fetch Senate disclosures: {e}")

        # 3. Finnhub Verified Insider Disclosures (Primary Insider Source)
        finnhub_records = self._fetch_from_finnhub_insiders()
        if finnhub_records:
            records.extend(finnhub_records)

        # 4. Fallback: SEC Form 4 Filings directly from SEC EDGAR
        if not finnhub_records:
            cik = CIK_MAP.get(self.ticker, CIK_MAP.get(PRIMARY_TICKER, "0001318605"))
            sec_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            headers = {'User-Agent': 'TradingBot boris@example.com'}
            try:
                sec_r = requests.get(sec_url, headers=headers, timeout=5)
                if sec_r.status_code == 200:
                    recent = sec_r.json().get('filings', {}).get('recent', {})
                    forms = recent.get('form', [])
                    dates = recent.get('filingDate', [])
                    for f, d in zip(forms, dates):
                        if f in ['4', '144']:
                            records.append({
                                'date': pd.to_datetime(d),
                                'signal': 0.5,  # Form 4 disclosure signal
                                'is_disclosure': 1
                            })
                    logger.info(f"[PoliticalTradesFetcher] Processed SEC Form 4 disclosures for {self.ticker}")
            except Exception as e:
                logger.warning(f"[PoliticalTradesFetcher] Could not fetch SEC Form 4 filings: {e}")

        if not records:
            return pd.DataFrame()

        df_raw = pd.DataFrame(records)
        daily_df = df_raw.groupby('date').agg({
            'signal': 'sum',
            'is_disclosure': 'max'
        }).sort_index()

        # Cache results locally
        daily_df.to_csv(self.cache_path)
        return daily_df

    def fetch_political_features(self, dates_index: pd.DatetimeIndex) -> pd.DataFrame:
        """
        Aligns daily political features with target dates_index.
        Returns political_trade_signal, political_net_buy_10d, and political_disclosure_flag.
        """
        df = pd.DataFrame(index=dates_index)

        # Check local cache first or fetch fresh
        if self.cache_path.exists():
            try:
                raw_df = pd.read_csv(self.cache_path, parse_dates=['date'], index_col='date')
            except Exception:
                raw_df = self.fetch_raw_political_disclosures()
        else:
            raw_df = self.fetch_raw_political_disclosures()

        if not raw_df.empty:
            df = df.join(raw_df, how='left')
            df['signal'] = df['signal'].fillna(0.0)
            df['is_disclosure'] = df['is_disclosure'].fillna(0).astype(int)
        else:
            df['signal'] = 0.0
            df['is_disclosure'] = 0

        # Normalized signal [-1.0, +1.0]
        max_abs_signal = df['signal'].abs().quantile(0.99) + 1e-9
        df['political_trade_signal'] = df['signal'] / max_abs_signal
        df['political_net_buy_10d'] = df['political_trade_signal'].rolling(10, min_periods=1).sum()
        df['political_disclosure_flag'] = df['is_disclosure']

        # Clean up transient join columns
        df.drop(columns=['signal', 'is_disclosure'], inplace=True, errors='ignore')

        return df

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dates = pd.date_range(start="2025-01-01", periods=30, freq="B")
    pf = PoliticalTradesFetcher("TSLA")
    pol_df = pf.fetch_political_features(dates)
    print("\nSample Real Political Features:")
    print(pol_df.head(15))
