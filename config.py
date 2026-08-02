import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data_store"
DATA_DIR.mkdir(exist_ok=True)

# Primary Asset Settings
PRIMARY_TICKER = "TSLA"
BENCHMARK_TICKERS = ["SPY", "QQQ", "^VIX"]

# Date Range: 2025 onwards as specified
START_DATE = "2025-01-01"

# Swing Target Definition
SWING_HORIZON_DAYS = 5      # 5 trading days horizon
SWING_UP_THRESHOLD = 0.05   # +5% target for Swing Up
SWING_DOWN_THRESHOLD = -0.05 # -5% target for Swing Down

# Feature Configs
FEATURE_CHANNELS = {
    "technicals": True,
    "market_macro": True,
    "news_sentiment": True,
    "political_trades": True,
    "social_sentiment": True
}

# Walk-Forward Backtest Settings
TRAIN_WINDOW_DAYS = 60      # Rolling training context window for TabFM
RETRAIN_EVERY_N_DAYS = 5    # Retrain/update model every 5 trading days
TEST_HORIZON = 1
DEFAULT_CONFIDENCE_THRESHOLD = 0.62 # High-conviction threshold for signal generation
