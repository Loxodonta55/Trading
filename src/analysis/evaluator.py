import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from src.features.builder import FeatureBuilder
from src.features.calibrator import FeatureCalibrator
from src.backtest.engine import WalkForwardBacktester

from config import DEFAULT_CONFIDENCE_THRESHOLD

class SensitivityEvaluator:
    """
    Evaluates multi-source feature subsets, calibrates top features per asset ticker,
    and compares TabFM performance against traditional ML models.
    """
    def __init__(self, confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD, top_k: int = 15):
        self.confidence_threshold = confidence_threshold
        self.top_k = top_k
        self.calibrator = FeatureCalibrator(top_k=top_k)
        self.backtester = WalkForwardBacktester(confidence_threshold=confidence_threshold)

    def run_ablation_experiments(self, df: pd.DataFrame = None, ticker: str = "TSLA") -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        # Run Automated Stock Feature Calibration
        df, calibrated_features, importances = self.calibrator.calibrate_features_for_ticker(ticker=ticker, df=df)
        best_features = calibrated_features

        # 1. Compare Model Architectures & Target Thresholds (5% vs 8%)
        models_to_test = [
            ("1. TabFM (Standard 5% Swing Target)", "TabFM", "swing_target_5pct"),
            ("2. TabFM (Strong 8% Swing Target)", "TabFM", "swing_target_8pct"),
            ("3. XGBoost (Standard 5% Swing Target)", "gbm", "swing_target_5pct"),
            ("4. XGBoost (Strong 8% Swing Target)", "gbm", "swing_target_8pct"),
            ("5. Random Forest (Strong 8% Swing Target)", "random_forest", "swing_target_8pct"),
            ("6. Logistic Regression (Strong 8% Swing Target)", "logistic", "swing_target_8pct")
        ]

        results_summary = []
        experiment_dfs = {}

        print("\n==================================================")
        print("TARGET THRESHOLD COMPARISON (5% vs 8% SWING LABELS)")
        print("==================================================")

        for exp_name, model_key, target_col in models_to_test:
            print(f"\n[Evaluator] Running Backtest for: {exp_name} (Target: {target_col})")
            res_df, metrics = self.backtester.run_backtest(
                df, 
                feature_cols=best_features, 
                model_name=model_key, 
                target_col=target_col
            )
            
            metrics['experiment'] = exp_name
            metrics['num_features'] = len(best_features)
            results_summary.append(metrics)
            experiment_dfs[exp_name] = res_df

        summary_df = pd.DataFrame(results_summary)
        cols_order = ['experiment', 'num_features', 'sharpe_ratio', 'win_rate', 'total_return', 'profit_factor', 'max_drawdown', 'n_trades']
        summary_df = summary_df[cols_order]

        print("\n==================================================")
        print("SWING TARGET THRESHOLD BENCHMARK SUMMARY (5% vs 8%)")
        print("==================================================")
        print(summary_df.to_string(index=False))

        return summary_df, experiment_dfs

if __name__ == "__main__":
    evaluator = SensitivityEvaluator()
    summary, _ = evaluator.run_ablation_experiments()
