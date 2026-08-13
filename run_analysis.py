import os
import sys
import json
import logging
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, Optional

from src.features.builder import FeatureBuilder
from src.backtest.engine import WalkForwardBacktester
from src.analysis.evaluator import SensitivityEvaluator
from src.data.db_manager import DatabaseManager
from config import DATA_DIR

logger = logging.getLogger(__name__)


def _safe_float(row: pd.Series, col: str, default: float = 0.0) -> float:
    """Helper to safely extract float from row."""
    val = row.get(col, default)
    if pd.isna(val):
        return default
    return float(val)

def _safe_int(row: pd.Series, col: str, default: int = 0) -> int:
    """Helper to safely extract int from row."""
    val = row.get(col, default)
    if pd.isna(val):
        return default
    return int(val)


def _needs_update(db: DatabaseManager) -> bool:
    """
    Check if the pipeline needs to run by comparing the last pipeline run date
    against the current date. Skips weekends/holidays awareness — simply checks
    if at least one new trading day may have occurred since the last run.
    """
    last_run = db.get_metadata("pipeline_last_run_date")
    if not last_run:
        logger.info("[Pipeline] No previous run recorded. Full run needed.")
        return True

    last_run_date = datetime.strptime(last_run, "%Y-%m-%d").date()
    today = datetime.now().date()
    days_since = (today - last_run_date).days

    if days_since <= 0:
        logger.info(f"[Pipeline] Already ran today ({last_run}). No update needed.")
        return False

    logger.info(f"[Pipeline] Last run: {last_run} ({days_since} days ago). Update needed.")
    return True


def _purge_caches_for_full_run() -> None:
    """Delete cached CSV files to force a complete re-download from START_DATE."""
    cache_files = list(DATA_DIR.glob("*_daily.csv")) + list(DATA_DIR.glob("benchmarks_daily.csv"))
    for f in cache_files:
        logger.info(f"[Pipeline] Purging cache: {f.name}")
        f.unlink(missing_ok=True)


def run_main_pipeline(force: bool = False, full: bool = False) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Runs the main analysis pipeline for feature engineering, calibration,
    and backtesting.

    Args:
        force: If True, run even if data appears up-to-date.
        full:  If True, delete all caches and re-download from START_DATE.

    Returns:
        A tuple containing multi-ticker data and dashboard export data.
    """
    logger.info("\n========================================================")
    logger.info("  TABFM TESLA & ALPHABET SWING PREDICTION ENGINE        ")
    logger.info("========================================================\n")
    
    db = DatabaseManager()

    # --- Delta check: skip if already up-to-date ---
    if not force and not full and not _needs_update(db):
        # Load existing dashboard data and return it
        json_path = Path(__file__).resolve().parent / "web" / "backtest_dashboard_data.json"
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info("[Pipeline] Data is current. Returning cached dashboard data.")
            return data.get("data", {}), data
        # If JSON doesn't exist, fall through to full run
        logger.info("[Pipeline] No cached JSON found despite recent run date. Running pipeline.")

    # --- Full mode: purge all caches ---
    if full:
        logger.info("[Pipeline] FULL MODE: Purging all cached data for fresh download...")
        _purge_caches_for_full_run()
        # Clear last-data-date metadata so fetcher does initial download
        for ticker in ["TSLA", "GOOGL", "SPCX", "NVDA"]:
            db.set_metadata(f"last_data_date_{ticker}", "")

    evaluator = SensitivityEvaluator()

    tickers = ["TSLA", "GOOGL", "SPCX", "NVDA"]
    multi_ticker_data = {}

    for ticker in tickers:
        logger.info(f"\n>>> Running Feature Engineering & Evaluation Pipeline for: {ticker} <<<")
        builder = FeatureBuilder(ticker=ticker)
        df = builder.build_dataset()
        db.save_features(df, ticker=ticker)

        summary_df, exp_dfs = evaluator.run_ablation_experiments(df=df, ticker=ticker)

        best_exp_name = summary_df.sort_values(by='sharpe_ratio', ascending=False).iloc[0]['experiment']
        logger.info(f"[Pipeline] Best Feature Strategy for {ticker}: '{best_exp_name}'")
        best_df = exp_dfs[best_exp_name]

        for exp_name, exp_df in exp_dfs.items():
            db.save_predictions(exp_df, model_name=f"TabFM_{exp_name}", ticker=ticker)
        db.save_backtest_run(summary_df.to_dict(orient="records"))

        clean_summary = summary_df.fillna(0.0).to_dict(orient="records")
        chart_data = []

        for idx, row in best_df.iterrows():
            date_str = idx.strftime('%Y-%m-%d')
            
            chart_data.append({
                "date": date_str,
                "open": _safe_float(row, 'open'),
                "high": _safe_float(row, 'high'),
                "low": _safe_float(row, 'low'),
                "close": _safe_float(row, 'close'),
                "volume": _safe_int(row, 'volume'),
                "rsi_14": _safe_float(row, 'rsi_14', default=50.0),
                "news_sentiment": _safe_float(row, 'news_sentiment'),
                "news_sentiment_3d_ma": _safe_float(row, 'news_sentiment_3d_ma'),
                "political_trade_signal": _safe_int(row, 'political_trade_signal'),
                "x_sentiment_score": _safe_float(row, 'x_sentiment_score'),
                "options_iv_skew": _safe_float(row, 'options_iv_skew'),
                "put_call_oi_ratio": _safe_float(row, 'put_call_oi_ratio', default=1.0),
                "rel_strength_spy": _safe_float(row, 'tsla_vs_spy_rel_strength'),
                "swing_target": _safe_int(row, 'swing_target', default=1),
                "signal": _safe_int(row, 'signal'),
                "prob_up": _safe_float(row, 'prob_up'),
                "prob_down": _safe_float(row, 'prob_down'),
                "equity_curve": _safe_float(row, 'equity_curve', default=1.0),
                "buy_hold_equity": _safe_float(row, 'buy_hold_equity', default=1.0)
            })

        multi_ticker_data[ticker] = {
            "summary": clean_summary,
            "best_experiment": best_exp_name,
            "chart_data": chart_data
        }

    dashboard_export = {
        "tickers": tickers,
        "data": multi_ticker_data,
        "summary": multi_ticker_data[tickers[0]]["summary"],
        "best_experiment": multi_ticker_data[tickers[0]]["best_experiment"],
        "tsla_chart_data": multi_ticker_data[tickers[0]]["chart_data"]
    }

    export_file = DATA_DIR / "backtest_dashboard_data.json"
    with open(export_file, "w") as f:
        json.dump(dashboard_export, f, indent=2)

    web_export_file = Path(__file__).resolve().parent / "web" / "backtest_dashboard_data.json"
    web_export_file.parent.mkdir(exist_ok=True)
    with open(web_export_file, "w") as f:
        json.dump(dashboard_export, f, indent=2)

    # Record successful run timestamp
    db.set_metadata("pipeline_last_run_date", datetime.now().strftime("%Y-%m-%d"))
    db.set_metadata("pipeline_last_run_ts", datetime.now().isoformat())

    logger.info(f"\n[Pipeline] Successfully exported multi-ticker dashboard data to: {export_file} and {web_export_file}")
    logger.info(f"[Pipeline] Database persistence active at: {db.db_path}")
    return multi_ticker_data, dashboard_export


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TabFM Trading Analysis Pipeline")
    parser.add_argument(
        "--full", action="store_true",
        help="Purge all caches and re-download data from START_DATE. Full re-computation."
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Force pipeline run even if data appears up-to-date today."
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    run_main_pipeline(force=args.force, full=args.full)
