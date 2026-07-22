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
    print("  TABFM TESLA SWING PREDICTION & BACKTESTING ENGINE    ")
    print("========================================================\n")
    
    # 0. Initialize Database
    db = DatabaseManager()

    # 1. Feature Engineering (Inputs)
    builder = FeatureBuilder()
    df = builder.build_dataset()
    db.save_features(df, ticker="TSLA")

    # 2. Run Sensitivity Ablation Study
    evaluator = SensitivityEvaluator()
    summary_df, exp_dfs = evaluator.run_ablation_experiments()

    # Select Best Feature Model Results for Dashboard Export
    best_exp_name = summary_df.sort_values(by='sharpe_ratio', ascending=False).iloc[0]['experiment']
    print(f"\n[Pipeline] Best Feature Strategy: '{best_exp_name}'")

    best_df = exp_dfs[best_exp_name]

    # Save Predictions (Outputs) for all experiments and Backtest Run Summaries to DB
    for exp_name, exp_df in exp_dfs.items():
        db.save_predictions(exp_df, model_name=f"TabFM_{exp_name}", ticker="TSLA")
    db.save_backtest_run(summary_df.to_dict(orient="records"))

    # Clean summary dataframe from NaN
    clean_summary = summary_df.fillna(0.0).to_dict(orient="records")

    dashboard_export = {
        "summary": clean_summary,
        "best_experiment": best_exp_name,
        "tsla_chart_data": []
    }

    for idx, row in best_df.iterrows():
        date_str = idx.strftime('%Y-%m-%d')
        eq_val = float(row['equity_curve']) if not pd.isna(row['equity_curve']) else 1.0
        bh_val = float(row['buy_hold_equity']) if not pd.isna(row['buy_hold_equity']) else 1.0
        
        dashboard_export["tsla_chart_data"].append({
            "date": date_str,
            "open": float(row['open']) if not pd.isna(row['open']) else 0.0,
            "high": float(row['high']) if not pd.isna(row['high']) else 0.0,
            "low": float(row['low']) if not pd.isna(row['low']) else 0.0,
            "close": float(row['close']) if not pd.isna(row['close']) else 0.0,
            "volume": int(row['volume']) if not pd.isna(row['volume']) else 0,
            "rsi_14": float(row['rsi_14']) if not pd.isna(row['rsi_14']) else 50.0,
            "news_sentiment": float(row['news_sentiment']) if ('news_sentiment' in row and not pd.isna(row['news_sentiment'])) else 0.0,
            "political_trade_signal": int(row['political_trade_signal']) if ('political_trade_signal' in row and not pd.isna(row['political_trade_signal'])) else 0,
            "x_sentiment_score": float(row['x_sentiment_score']) if ('x_sentiment_score' in row and not pd.isna(row['x_sentiment_score'])) else 0.0,
            "swing_target": int(row['swing_target']) if not pd.isna(row['swing_target']) else 1,
            "signal": int(row['signal']) if not pd.isna(row['signal']) else 0,
            "prob_up": float(row['prob_up']) if not pd.isna(row['prob_up']) else 0.0,
            "prob_down": float(row['prob_down']) if not pd.isna(row['prob_down']) else 0.0,
            "equity_curve": eq_val,
            "buy_hold_equity": bh_val
        })

    export_file = DATA_DIR / "backtest_dashboard_data.json"
    with open(export_file, "w") as f:
        json.dump(dashboard_export, f, indent=2)

    web_export_file = Path(__file__).resolve().parent / "web" / "backtest_dashboard_data.json"
    web_export_file.parent.mkdir(exist_ok=True)
    with open(web_export_file, "w") as f:
        json.dump(dashboard_export, f, indent=2)

    print(f"\n[Pipeline] Successfully exported dashboard data to: {export_file} and {web_export_file}")
    print(f"[Pipeline] Database persistence active at: {db.db_path}")
    return summary_df, dashboard_export

if __name__ == "__main__":
    run_main_pipeline()
