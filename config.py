"""
Configuration module for the Trading project.
Defines base paths, assets, parameters, and settings.
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = BASE_DIR / "data_store"

# Automatically load .env file if present
load_dotenv(BASE_DIR / ".env")

logger = logging.getLogger(__name__)

def init_config() -> None:
    """Initialize configuration dependencies (e.g. create directories)."""
    DATA_DIR.mkdir(exist_ok=True)

# Primary Asset Settings
PRIMARY_TICKER: str = "TSLA"
BENCHMARK_TICKERS: list[str] = ["SPY", "QQQ", "^VIX"]

# Date Range: 2025 onwards as specified
START_DATE: str = "2025-01-01"

# Swing Target Definition
SWING_HORIZON_DAYS: int = 5      # 5 trading days horizon
SWING_UP_THRESHOLD: float = 0.05   # +5% target for Swing Up
SWING_DOWN_THRESHOLD: float = -0.05 # -5% target for Swing Down

# Feature Configs
FEATURE_CHANNELS: dict[str, bool] = {
    "technicals": True,
    "market_macro": True,
    "news_sentiment": True,
    "political_trades": True,
    "social_sentiment": True
}

# Walk-Forward Backtest Settings
TRAIN_WINDOW_DAYS: int = 120     # Rolling training context window for TabFM (increased from 60 for better sample/feature ratio)
RETRAIN_EVERY_N_DAYS: int = 5    # Retrain/update model every 5 trading days
TEST_HORIZON: int = 1
DEFAULT_CONFIDENCE_THRESHOLD: float = 0.62 # High-conviction threshold for signal generation

# Interactive Brokers (IBKR) Integration Settings
IBKR_HOST: str = os.getenv("IBKR_HOST", "127.0.0.1")
IBKR_PORT: int = int(os.getenv("IBKR_PORT", "7497"))  # 7497 = Paper, 7496 = Live, 4001 = IB Gateway
IBKR_CLIENT_ID: int = int(os.getenv("IBKR_CLIENT_ID", "1"))
IBKR_ACCOUNT: str = os.getenv("IBKR_ACCOUNT", "")       # Optional specific account ID filter
IBKR_CONNECT_TIMEOUT: int = int(os.getenv("IBKR_CONNECT_TIMEOUT", "10"))

# Alternative Data API Keys (Phase 3 Institutional Edge)
QUIVER_API_KEY: str = os.getenv("QUIVER_API_KEY", "")                 # Quiver Quantitative (Congress/Lobbying)
UNUSUAL_WHALES_API_KEY: str = os.getenv("UNUSUAL_WHALES_API_KEY", "") # Unusual Whales (Options Flow/Dark Pool)
POLYGON_API_KEY: str = os.getenv("POLYGON_API_KEY", "")               # Polygon.io (Realtime Options & Equities)
FINNHUB_API_KEY: str = os.getenv("FINNHUB_API_KEY", "")               # Finnhub (Live News Sentiment & Earnings)
ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")   # Alpha Vantage (Historical Sentiment & Macro)



