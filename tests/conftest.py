"""Shared test fixtures for the Trading Intelligence Platform test suite."""
import pytest
import pandas as pd
import numpy as np
import sqlite3
import tempfile
from pathlib import Path


@pytest.fixture
def sample_price_df() -> pd.DataFrame:
    """Creates a realistic sample price DataFrame with OHLCV data."""
    np.random.seed(42)
    dates = pd.date_range(start="2025-01-02", periods=100, freq="B")
    base_price = 250.0
    returns = np.random.normal(0.001, 0.02, 100)
    closes = base_price * np.cumprod(1 + returns)

    df = pd.DataFrame({
        "open": closes * (1 + np.random.normal(0, 0.005, 100)),
        "high": closes * (1 + np.abs(np.random.normal(0, 0.01, 100))),
        "low": closes * (1 - np.abs(np.random.normal(0, 0.01, 100))),
        "close": closes,
        "volume": np.random.randint(10_000_000, 50_000_000, 100),
    }, index=dates)
    df.index.name = "date"
    return df


@pytest.fixture
def sample_price_df_with_benchmarks(sample_price_df: pd.DataFrame) -> pd.DataFrame:
    """Extends sample price data with benchmark columns (SPY, VIX)."""
    np.random.seed(99)
    n = len(sample_price_df)
    df = sample_price_df.copy()
    df["spy_close"] = 450.0 * np.cumprod(1 + np.random.normal(0.0005, 0.01, n))
    df["qqq_close"] = 380.0 * np.cumprod(1 + np.random.normal(0.0005, 0.012, n))
    df["vix_close"] = 18.0 + np.random.normal(0, 2, n)
    return df


@pytest.fixture
def sample_features_df(sample_price_df_with_benchmarks: pd.DataFrame) -> pd.DataFrame:
    """Creates a DataFrame with pre-computed features for model testing."""
    df = sample_price_df_with_benchmarks.copy()
    np.random.seed(123)
    n = len(df)

    # Technical features
    df["rsi_14"] = 50 + np.random.normal(0, 15, n)
    df["macd"] = np.random.normal(0, 2, n)
    df["macd_signal"] = np.random.normal(0, 1.5, n)
    df["macd_hist"] = df["macd"] - df["macd_signal"]
    df["atr_14"] = np.abs(np.random.normal(5, 2, n))
    df["atr_ratio"] = df["atr_14"] / df["close"]
    df["bollinger_pos"] = np.random.uniform(0, 1, n)
    df["bollinger_width"] = np.random.uniform(0.02, 0.08, n)
    df["volume_ratio_5d"] = np.random.uniform(0.5, 2.0, n)

    # News & sentiment features
    df["news_sentiment"] = np.random.uniform(-0.5, 0.5, n)
    df["news_sentiment_3d_ma"] = df["news_sentiment"].rolling(3, min_periods=1).mean()
    df["press_release_flag"] = np.random.choice([0, 1], n, p=[0.85, 0.15])
    df["news_volume"] = np.random.poisson(12, n)
    df["political_trade_signal"] = np.random.choice([-1, 0, 1], n, p=[0.08, 0.84, 0.08])
    df["x_sentiment_score"] = np.random.uniform(-0.5, 0.5, n)

    # Options features
    df["put_call_oi_ratio"] = np.random.uniform(0.5, 1.5, n)
    df["put_call_vol_ratio"] = np.random.uniform(0.5, 1.5, n)
    df["options_iv_skew"] = np.random.normal(0, 0.05, n)
    df["options_smart_money_bullish"] = np.random.choice([0, 1], n)

    # SEC features
    df["sec_filing_flag"] = np.random.choice([0, 1], n, p=[0.9, 0.1])
    df["sec_8k_flag"] = 0
    df["sec_form4_insider_flag"] = 0
    df["sec_10k_10q_flag"] = 0
    df["sec_filing_count_30d"] = np.random.randint(0, 5, n)
    df["days_since_last_sec_filing"] = np.random.randint(1, 60, n)
    df["sec_mda_uncertainty_score"] = np.random.uniform(0, 5, n)
    df["sec_mda_optimism_score"] = np.random.uniform(0, 5, n)
    df["sec_text_risk_drift"] = np.random.uniform(0, 0.5, n)

    # Macro
    df["spy_return_1d"] = df["spy_close"].pct_change().fillna(0)
    df["tsla_vs_spy_rel_strength"] = df["close"].pct_change().fillna(0) - df["spy_return_1d"]
    df["vix_change_1d"] = df["vix_close"].pct_change().fillna(0)

    # Targets
    df["swing_target"] = np.random.choice([0, 1, 2], n, p=[0.2, 0.6, 0.2])
    df["swing_target_5pct"] = df["swing_target"]
    df["swing_target_8pct"] = np.random.choice([0, 1, 2], n, p=[0.15, 0.7, 0.15])
    df["forward_max_return"] = np.random.uniform(-0.1, 0.15, n)
    df["forward_min_return"] = np.random.uniform(-0.15, 0.05, n)

    return df


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Provides a temporary SQLite database path."""
    return tmp_path / "test_trading.db"


@pytest.fixture
def feature_column_names() -> list[str]:
    """Returns the standard list of feature column names used for model training."""
    return [
        "rsi_14", "macd", "macd_signal", "macd_hist",
        "atr_14", "atr_ratio", "bollinger_pos", "bollinger_width",
        "volume_ratio_5d", "news_sentiment", "news_sentiment_3d_ma",
        "put_call_oi_ratio", "options_iv_skew",
        "spy_return_1d", "vix_change_1d",
    ]
