import requests
import pandas as pd
import numpy as np
import re
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from config import DATA_DIR, PRIMARY_TICKER

# Financial Text Lexicons for SEC Filing Analysis
UNCERTAINTY_KEYWORDS = {
    'uncertainty', 'uncertainties', 'volatility', 'disruption', 'impairment', 'bottleneck',
    'delay', 'delays', 'litigation', 'lawsuit', 'investigation', 'adversely', 'adverse',
    'constraint', 'constraints', 'shortage', 'vulnerability', 'fluctuation', 'inflationary'
}

OPTIMISM_KEYWORDS = {
    'accelerating', 'expansion', 'record', 'profitability', 'profitable', 'breakthrough',
    'demand', 'efficiency', 'momentum', 'outperform', 'innovation', 'synergy', 'strong',
    'milestone', 'leadership', 'scaling', 'scaled', 'growth'
}

class SecTextProcessor:
    """
    Two-Stage Unstructured Data Engine:
    Stage 1: Downloads raw SEC EDGAR 10-K, 10-Q, and 8-K full-text HTML/XBRL documents into data_store/raw_sec_docs/
    Stage 2: Parses raw document text using NLP techniques to extract Risk Factors & MD&A Sentiment Scores.
    """
    def __init__(self, ticker: str = PRIMARY_TICKER, cik: str = "0001318605"):
        self.ticker = ticker
        self.cik = cik
        self.raw_docs_dir = DATA_DIR / "raw_sec_docs"
        self.raw_docs_dir.mkdir(exist_ok=True)
        self.processed_cache = DATA_DIR / f"{self.ticker}_sec_structured_text_features.csv"

    def _clean_html_text(self, raw_html: str) -> str:
        """Strips HTML/XBRL tags and normalizes whitespace."""
        text = re.sub(r'<[^>]+>', ' ', raw_html)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def collect_and_process_raw_filings(self, max_filings: int = 25) -> pd.DataFrame:
        """
        Stage 1 & 2: Ingests raw full-text documents from SEC EDGAR API,
        saves raw files to disk, and runs NLP structuring on text content.
        """
        print(f"[SecTextProcessor] Starting Unstructured Document Collector for {self.ticker}...")
        url = f"https://data.sec.gov/submissions/CIK{self.cik}.json"
        headers = {'User-Agent': 'TradingBot boris@example.com'}

        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200:
                print(f"[SecTextProcessor] SEC API returned status {r.status_code}")
                return self._load_cache_or_fallback()

            data = r.json()
            recent = data.get('filings', {}).get('recent', {})
            
            forms = recent.get('form', [])
            filing_dates = recent.get('filingDate', [])
            accession_nums = recent.get('accessionNumber', [])
            primary_docs = recent.get('primaryDocument', [])

            records = []
            prev_text_len = 0

            # Process top N recent filings
            for i in range(min(len(forms), max_filings)):
                form = str(forms[i]).upper().strip()
                date_str = filing_dates[i]
                acc_num = accession_nums[i].replace('-', '')
                doc_name = primary_docs[i]

                # Focus on major SEC documents: 8-K, 10-K, 10-Q, 4
                if not any(target in form for target in ['8-K', '10-K', '10-Q', '4']):
                    continue

                raw_file_path = self.raw_docs_dir / f"{date_str}_{form.replace('/', '_')}_{doc_name}"
                raw_text = ""

                # Stage 1: Download raw document if not cached
                if not raw_file_path.exists():
                    doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(self.cik)}/{acc_num}/{doc_name}"
                    try:
                        doc_res = requests.get(doc_url, headers=headers, timeout=10)
                        if doc_res.status_code == 200:
                            raw_text = doc_res.text
                            with open(raw_file_path, "w", encoding="utf-8") as f:
                                f.write(raw_text)
                    except Exception:
                        pass
                else:
                    try:
                        with open(raw_file_path, "r", encoding="utf-8") as f:
                            raw_text = f.read()
                    except Exception:
                        pass

                # Stage 2: Parse and Structure raw text
                clean_text = self._clean_html_text(raw_text)
                words = re.findall(r'\b[a-z]+\b', clean_text.lower())
                word_count = len(words)

                if word_count > 0:
                    unc_count = sum(1 for w in words if w in UNCERTAINTY_KEYWORDS)
                    opt_count = sum(1 for w in words if w in OPTIMISM_KEYWORDS)
                    
                    unc_score = float(unc_count / float(word_count)) * 1000.0
                    opt_score = float(opt_count / float(word_count)) * 1000.0
                    
                    # Risk text drift vs previous document
                    risk_drift = float(abs(word_count - prev_text_len) / float(word_count + prev_text_len + 1e-9))
                    prev_text_len = word_count
                else:
                    unc_score = 0.0
                    opt_score = 0.0
                    risk_drift = 0.0

                records.append({
                    'date': pd.to_datetime(date_str),
                    'sec_mda_uncertainty_score': unc_score,
                    'sec_mda_optimism_score': opt_score,
                    'sec_text_risk_drift': risk_drift
                })

            if not records:
                return self._load_cache_or_fallback()

            df_structured = pd.DataFrame(records)
            daily_sec_text = df_structured.groupby('date').mean()
            daily_sec_text.to_csv(self.processed_cache)
            print(f"[SecTextProcessor] Successfully processed & structured {len(records)} raw SEC documents.")
            return daily_sec_text

        except Exception as e:
            print(f"[SecTextProcessor] Could not process SEC raw text: {e}")
            return self._load_cache_or_fallback()

    def _load_cache_or_fallback(self) -> pd.DataFrame:
        if self.processed_cache.exists():
            df = pd.read_csv(self.processed_cache)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            return df
        return pd.DataFrame()

    def fetch_sec_text_features(self, dates_index: pd.DatetimeIndex) -> pd.DataFrame:
        """
        Aligns structured SEC text features with the target dates_index.
        Applies forward fill to simulate active information persistence.
        """
        df = pd.DataFrame(index=dates_index)
        structured_sec = self.collect_and_process_raw_filings()

        if not structured_sec.empty:
            df = df.join(structured_sec, how='left')
            df['sec_mda_uncertainty_score'] = df['sec_mda_uncertainty_score'].ffill().fillna(0.0)
            df['sec_mda_optimism_score'] = df['sec_mda_optimism_score'].ffill().fillna(0.0)
            df['sec_text_risk_drift'] = df['sec_text_risk_drift'].fillna(0.0)
        else:
            df['sec_mda_uncertainty_score'] = 0.0
            df['sec_mda_optimism_score'] = 0.0
            df['sec_text_risk_drift'] = 0.0

        return df

if __name__ == "__main__":
    dates = pd.date_range(start="2025-01-01", periods=30, freq="B")
    processor = SecTextProcessor()
    text_df = processor.fetch_sec_text_features(dates)
    print("\nSample Structured SEC Text Features:")
    print(text_df.head(10))
