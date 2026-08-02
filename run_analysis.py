import os
import json
import sys
import pandas as pd
import numpy as np
from pathlib import Path

from src.features.builder import FeatureBuilder
from src.backtest.engine import WalkForwardBacktester
from src.analysis.evaluator import SensitivityEvaluator
from src.data.db_manager import DatabaseManager
from config import DATA_DIR

def run_main_pipeline():
    print("\n========================================================")
    print("  TABFM TESLA & ALPHABET SWING PREDICTION ENGINE        ")
    print("========================================================\n")
    
    db = DatabaseManager()
    evaluator = SensitivityEvaluator()

    tickers = ["TSLA", "GOOGL", "SPCX", "NVDA"]
    multi_ticker_data = {}

    for ticker in tickers:
        print(f"\n>>> Running Feature Engineering & Evaluation Pipeline for: {ticker} <<<")
        builder = FeatureBuilder(ticker=ticker)
        df = builder.build_dataset()
        db.save_features(df, ticker=ticker)

        summary_df, exp_dfs = evaluator.run_ablation_experiments(df=df, ticker=ticker)

        best_exp_name = summary_df.sort_values(by='sharpe_ratio', ascending=False).iloc[0]['experiment']
        print(f"[Pipeline] Best Feature Strategy for {ticker}: '{best_exp_name}'")
        best_df = exp_dfs[best_exp_name]

        for exp_name, exp_df in exp_dfs.items():
            db.save_predictions(exp_df, model_name=f"TabFM_{exp_name}", ticker=ticker)
        db.save_backtest_run(summary_df.to_dict(orient="records"))

        clean_summary = summary_df.fillna(0.0).to_dict(orient="records")
        chart_data = []

        for idx, row in best_df.iterrows():
            date_str = idx.strftime('%Y-%m-%d')
            eq_val = float(row['equity_curve']) if not pd.isna(row['equity_curve']) else 1.0
            bh_val = float(row['buy_hold_equity']) if not pd.isna(row['buy_hold_equity']) else 1.0
            
            chart_data.append({
                "date": date_str,
                "open": float(row['open']) if not pd.isna(row['open']) else 0.0,
                "high": float(row['high']) if not pd.isna(row['high']) else 0.0,
                "low": float(row['low']) if not pd.isna(row['low']) else 0.0,
                "close": float(row['close']) if not pd.isna(row['close']) else 0.0,
                "volume": int(row['volume']) if not pd.isna(row['volume']) else 0,
                "rsi_14": float(row['rsi_14']) if not pd.isna(row['rsi_14']) else 50.0,
                "news_sentiment": float(row['news_sentiment']) if ('news_sentiment' in row and not pd.isna(row['news_sentiment'])) else 0.0,
                "news_sentiment_3d_ma": float(row['news_sentiment_3d_ma']) if ('news_sentiment_3d_ma' in row and not pd.isna(row['news_sentiment_3d_ma'])) else 0.0,
                "political_trade_signal": int(row['political_trade_signal']) if ('political_trade_signal' in row and not pd.isna(row['political_trade_signal'])) else 0,
                "x_sentiment_score": float(row['x_sentiment_score']) if ('x_sentiment_score' in row and not pd.isna(row['x_sentiment_score'])) else 0.0,
                "options_iv_skew": float(row['options_iv_skew']) if ('options_iv_skew' in row and not pd.isna(row['options_iv_skew'])) else 0.0,
                "put_call_oi_ratio": float(row['put_call_oi_ratio']) if ('put_call_oi_ratio' in row and not pd.isna(row['put_call_oi_ratio'])) else 1.0,
                "rel_strength_spy": float(row['tsla_vs_spy_rel_strength']) if ('tsla_vs_spy_rel_strength' in row and not pd.isna(row['tsla_vs_spy_rel_strength'])) else 0.0,
                "swing_target": int(row['swing_target']) if not pd.isna(row['swing_target']) else 1,
                "signal": int(row['signal']) if not pd.isna(row['signal']) else 0,
                "prob_up": float(row['prob_up']) if not pd.isna(row['prob_up']) else 0.0,
                "prob_down": float(row['prob_down']) if not pd.isna(row['prob_down']) else 0.0,
                "equity_curve": eq_val,
                "buy_hold_equity": bh_val
            })

        multi_ticker_data[ticker] = {
            "summary": clean_summary,
            "best_experiment": best_exp_name,
            "tsla_chart_data": chart_data
        }

    dashboard_export = {
        "tickers": tickers,
        "data": multi_ticker_data,
        "summary": multi_ticker_data["TSLA"]["summary"],
        "best_experiment": multi_ticker_data["TSLA"]["best_experiment"],
        "tsla_chart_data": multi_ticker_data["TSLA"]["tsla_chart_data"]
    }

    export_file = DATA_DIR / "backtest_dashboard_data.json"
    with open(export_file, "w") as f:
        json.dump(dashboard_export, f, indent=2)

    web_export_file = Path(__file__).resolve().parent / "web" / "backtest_dashboard_data.json"
    web_export_file.parent.mkdir(exist_ok=True)
    with open(web_export_file, "w") as f:
        json.dump(dashboard_export, f, indent=2)

    print(f"\n[Pipeline] Successfully exported multi-ticker dashboard data to: {export_file} and {web_export_file}")
    print(f"[Pipeline] Database persistence active at: {db.db_path}")
    return multi_ticker_data, dashboard_export

if __name__ == "__main__":
    run_main_pipeline()
