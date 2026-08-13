import sqlite3
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional, Any, List, Dict

from config import DATA_DIR

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    SQLite-backed database manager for local, zero-cost, high-performance 
    storage of structured market features, model predictions, and backtest metrics.
    Supports incremental delta updates (UPSERT).
    """
    def __init__(self, db_path: Optional[Path] = None) -> None:
        if db_path is None:
            self.db_path = DATA_DIR / "trading_data.db"
        else:
            self.db_path = db_path
        self._init_db()

    def __enter__(self) -> 'DatabaseManager':
        """Enter context manager."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager."""
        pass

    def _get_connection(self) -> sqlite3.Connection:
        """Get a new SQLite connection."""
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        """Initialize relational database schema if not already existing."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Table for Market Features (Inputs)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_features (
                date TEXT NOT NULL,
                ticker TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                rsi_14 REAL,
                macd REAL,
                macd_signal REAL,
                macd_hist REAL,
                atr_14 REAL,
                atr_ratio REAL,
                bollinger_pos REAL,
                bollinger_width REAL,
                volume_ratio_5d REAL,
                spy_close REAL,
                spy_return_1d REAL,
                tsla_vs_spy_rel_strength REAL,
                vix_close REAL,
                vix_change_1d REAL,
                sec_filing_flag INTEGER,
                sec_8k_flag INTEGER,
                sec_form4_insider_flag INTEGER,
                sec_10k_10q_flag INTEGER,
                sec_filing_count_30d INTEGER,
                days_since_last_sec_filing INTEGER,
                sec_mda_uncertainty_score REAL,
                sec_mda_optimism_score REAL,
                sec_text_risk_drift REAL,
                put_call_oi_ratio REAL,
                put_call_vol_ratio REAL,
                options_iv_skew REAL,
                options_smart_money_bullish INTEGER,
                news_sentiment REAL,
                political_trade_signal INTEGER,
                x_sentiment_score REAL,
                swing_target INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (date, ticker)
            );
            """)

            # 2. Table for Model Predictions (Outputs)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS swing_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                ticker TEXT NOT NULL,
                model_name TEXT NOT NULL,
                swing_target INTEGER,
                predicted_signal INTEGER,
                prob_down REAL,
                prob_neutral REAL,
                prob_up REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, ticker, model_name) ON CONFLICT REPLACE
            );
            """)

            # 3. Table for Backtest Performance Summaries
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS backtest_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                experiment_name TEXT NOT NULL,
                num_features INTEGER,
                total_return REAL,
                win_rate REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                n_trades INTEGER,
                profit_factor REAL
            );
            """)

            # 4. Table for Pipeline Metadata and Persistent State Tracking
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            conn.commit()

    def save_features(self, df: pd.DataFrame, ticker: str = "TSLA") -> None:
        """Save/update feature dataset to SQLite database using UPSERT (INSERT OR REPLACE)."""
        save_df = df.copy()
        if 'date' not in save_df.columns:
            save_df = save_df.reset_index()
        
        save_df['date'] = save_df['date'].astype(str)
        save_df['ticker'] = ticker

        with self._get_connection() as conn:
            existing_cols = [c[1] for c in conn.execute("PRAGMA table_info(market_features)").fetchall()]
            valid_cols = [c for c in save_df.columns if c in existing_cols]
            
            # Upsert rows into market_features table without wiping historical data
            col_names = ", ".join(valid_cols)
            placeholders = ", ".join(["?"] * len(valid_cols))
            sql = f"INSERT OR REPLACE INTO market_features ({col_names}) VALUES ({placeholders})"
            
            records = save_df[valid_cols].values.tolist()
            conn.executemany(sql, records)
            conn.commit()
            logger.info(f"[DatabaseManager] Delta/Upsert: Saved {len(save_df)} feature rows for {ticker} to DB.")

    def save_predictions(self, results_df: pd.DataFrame, model_name: str = "TabFM", ticker: str = "TSLA") -> None:
        """Save model predictions to SQLite database with UPSERT (ON CONFLICT REPLACE)."""
        records = []
        for idx, row in results_df.iterrows():
            date_str = str(idx.date()) if hasattr(idx, 'date') else str(idx)
            records.append({
                'date': date_str,
                'ticker': ticker,
                'model_name': model_name,
                'swing_target': int(row['swing_target']),
                'predicted_signal': int(row['signal']),
                'prob_down': float(row['prob_down']),
                'prob_neutral': float(1.0 - row['prob_up'] - row['prob_down']),
                'prob_up': float(row['prob_up'])
            })
        
        pred_df = pd.DataFrame(records)
        with self._get_connection() as conn:
            cols = ['date', 'ticker', 'model_name', 'swing_target', 'predicted_signal', 'prob_down', 'prob_neutral', 'prob_up']
            col_names = ", ".join(cols)
            placeholders = ", ".join(["?"] * len(cols))
            sql = f"INSERT OR REPLACE INTO swing_predictions ({col_names}) VALUES ({placeholders})"
            conn.executemany(sql, pred_df[cols].values.tolist())
            conn.commit()

    def save_backtest_run(self, summary_records: List[Dict[str, Any]]) -> None:
        """Save backtest run summary to database."""
        summary_df = pd.DataFrame(summary_records)
        if 'experiment' in summary_df.columns:
            summary_df.rename(columns={'experiment': 'experiment_name'}, inplace=True)
        with self._get_connection() as conn:
            summary_df.to_sql('backtest_runs', conn, if_exists='replace', index=False)

    def load_features(self, ticker: str = "TSLA") -> pd.DataFrame:
        """Load features from database."""
        with self._get_connection() as conn:
            query = "SELECT * FROM market_features WHERE ticker = ? ORDER BY date ASC"
            df = pd.read_sql_query(query, conn, params=(ticker,), parse_dates=['date'])
            if not df.empty:
                df.set_index('date', inplace=True)
            return df

    def get_metadata(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get metadata value."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM pipeline_metadata WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else default

    def set_metadata(self, key: str, value: str) -> None:
        """Set metadata value."""
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO pipeline_metadata (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (key, str(value))
            )
            conn.commit()

    def get_last_data_date(self, ticker: str) -> Optional[str]:
        """Get last date for which data was fetched."""
        val = self.get_metadata(f"last_data_date_{ticker}")
        if val:
            return val
        
        # Fallback: check max date in market_features table
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(date) FROM market_features WHERE ticker = ?", (ticker,))
            row = cursor.fetchone()
            if row and row[0]:
                date_str = str(row[0])[:10]
                self.set_metadata(f"last_data_date_{ticker}", date_str)
                return date_str
        return None

    def set_last_data_date(self, ticker: str, date_str: str) -> None:
        """Set last date for which data was fetched."""
        self.set_metadata(f"last_data_date_{ticker}", date_str)

if __name__ == "__main__":
    db = DatabaseManager()
    logger.info("Database manager ready with UPSERT and pipeline_metadata support.")
