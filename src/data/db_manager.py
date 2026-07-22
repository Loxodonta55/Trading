import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

# Ensure config path is accessible
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from config import DATA_DIR

class DatabaseManager:
    """
    SQLite-backed database manager for local, zero-cost, high-performance 
    storage of structured market features, model predictions, and backtest metrics.
    """
    def __init__(self, db_path: Path = None):
        if db_path is None:
            self.db_path = DATA_DIR / "trading_data.db"
        else:
            self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initialize relational database schema if not already existing."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Table for Market Features (Inputs)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_features (
                date TEXT PRIMARY KEY,
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
                news_sentiment REAL,
                political_trade_signal INTEGER,
                x_sentiment_score REAL,
                swing_target INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            conn.commit()
            print(f"[DatabaseManager] Database initialized at: {self.db_path}")

    def save_features(self, df: pd.DataFrame, ticker: str = "TSLA"):
        """Save/update feature dataset to SQLite database."""
        save_df = df.copy()
        if 'date' not in save_df.columns:
            save_df = save_df.reset_index()
        
        save_df['date'] = save_df['date'].astype(str)
        save_df['ticker'] = ticker

        with self._get_connection() as conn:
            existing_cols = [c[1] for c in conn.execute("PRAGMA table_info(market_features)").fetchall()]
            valid_cols = [c for c in save_df.columns if c in existing_cols]
            
            # Clear existing rows for ticker to allow idempotent updates
            conn.execute("DELETE FROM market_features WHERE ticker = ?", (ticker,))
            save_df[valid_cols].to_sql('market_features', conn, if_exists='append', index=False, method='multi')
            print(f"[DatabaseManager] Saved {len(save_df)} feature rows to DB.")

    def save_predictions(self, results_df: pd.DataFrame, model_name: str = "TabFM", ticker: str = "TSLA"):
        """Save model predictions (Outputs) to SQLite database."""
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
            pred_df.to_sql('swing_predictions', conn, if_exists='append', index=False)
            print(f"[DatabaseManager] Saved {len(pred_df)} prediction records for {model_name} to DB.")

    def save_backtest_run(self, summary_records: list):
        """Save summary ablation results for a pipeline run."""
        summary_df = pd.DataFrame(summary_records)
        with self._get_connection() as conn:
            summary_df.to_sql('backtest_runs', conn, if_exists='append', index=False)
            print(f"[DatabaseManager] Saved {len(summary_df)} backtest run summaries to DB.")

    def load_features(self, ticker: str = "TSLA") -> pd.DataFrame:
        """Load stored market features from database."""
        with self._get_connection() as conn:
            query = "SELECT * FROM market_features WHERE ticker = ? ORDER BY date ASC"
            df = pd.read_sql_query(query, conn, params=(ticker,), parse_dates=['date'])
            if not df.empty:
                df.set_index('date', inplace=True)
            return df

    def load_predictions(self, model_name: str = "TabFM", ticker: str = "TSLA") -> pd.DataFrame:
        """Load stored predictions from database."""
        with self._get_connection() as conn:
            query = "SELECT * FROM swing_predictions WHERE ticker = ? AND model_name = ? ORDER BY date ASC"
            df = pd.read_sql_query(query, conn, params=(ticker, model_name), parse_dates=['date'])
            if not df.empty:
                df.set_index('date', inplace=True)
            return df

if __name__ == "__main__":
    db = DatabaseManager()
    print("Database manager ready.")
