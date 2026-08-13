import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path

from src.features.builder import FeatureBuilder
from src.features.calibrator import FeatureCalibrator
from src.backtest.engine import WalkForwardBacktester
from src.analysis.backtest_validator import BacktestValidator

from config import DEFAULT_CONFIDENCE_THRESHOLD

logger = logging.getLogger(__name__)

class SensitivityEvaluator:
    """
    Evaluates multi-source feature subsets, calibrates top features per asset ticker,
    and compares TabFM performance against traditional ML models.
    """
    def __init__(self, confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD, top_k: int = 15) -> None:
        """
        Initialize the evaluator.

        Args:
            confidence_threshold: Confidence threshold for backtester.
            top_k: Top K features to calibrate.
        """
        self.confidence_threshold = confidence_threshold
        self.top_k = top_k
        self.calibrator = FeatureCalibrator(top_k=top_k)
        self.backtester = WalkForwardBacktester(confidence_threshold=confidence_threshold)
        self.validator = BacktestValidator(n_simulations=500)

    def run_ablation_experiments(self, df: Optional[pd.DataFrame] = None, ticker: str = "TSLA") -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Runs ablation experiments comparing models and thresholds.

        Args:
            df: Pre-built feature dataframe.
            ticker: The ticker to evaluate.

        Returns:
            A tuple containing a summary dataframe and a dictionary of experiment result dataframes.
        """
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

        logger.info("\n==================================================")
        logger.info("TARGET THRESHOLD COMPARISON (5% vs 8% SWING LABELS)")
        logger.info("==================================================")

        for exp_name, model_key, target_col in models_to_test:
            logger.info(f"\n[Evaluator] Running Backtest for: {exp_name} (Target: {target_col})")
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

        logger.info("\n==================================================")
        logger.info("SWING TARGET THRESHOLD BENCHMARK SUMMARY (5% vs 8%)")
        logger.info("==================================================")
        logger.info("\n" + summary_df.to_string(index=False))

        # Run validation on the best experiment
        best_exp_name = summary_df.sort_values(by='sharpe_ratio', ascending=False).iloc[0]['experiment']
        best_df = experiment_dfs[best_exp_name]
        logger.info(f"\n[Evaluator] Running validation suite on best experiment: '{best_exp_name}'")
        validation_report = self.validator.full_validation_report(best_df)
        
        return summary_df, experiment_dfs

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    evaluator = SensitivityEvaluator()
    summary, _ = evaluator.run_ablation_experiments()
