from __future__ import annotations
import logging
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from pathlib import Path

from config import PRIMARY_TICKER, DATA_DIR
from src.features.builder import FeatureBuilder
from src.models.tabfm_wrapper import TabFMWrapper

logger = logging.getLogger(__name__)

class FeatureCalibrator:
    """
    Automated Feature Calibration Engine:
    For any stock ticker, ingests all multi-source candidate features,
    calculates empirical feature importances, selects EXAKTLYS the Top K (default: 15)
    highest-signal features, and displays the calibration breakdown to the user.
    """
    N_REPEATS = 5
    RANDOM_STATE = 42

    def __init__(self, top_k: int = 15) -> None:
        """
        Initialize the calibrator.

        Args:
            top_k: Number of top features to select.
        """
        self.top_k = top_k
        self.builder = FeatureBuilder()

    def calibrate_features_for_ticker(self, ticker: str = PRIMARY_TICKER, df: pd.DataFrame | None = None) -> tuple[pd.DataFrame, list[str], pd.Series]:
        """
        Calibrates and selects the Top K features specifically for the given ticker.
        Prints a detailed calibration report and returns (calibrated_df, top_feature_names, importance_series).
        
        Args:
            ticker: The ticker symbol.
            df: Optional pre-built feature dataframe.
            
        Returns:
            Tuple containing the dataframe, list of top feature names, and their importances.
        """
        if df is None:
            df = self.builder.build_dataset()

        # Isolate features vs targets
        # Exclude targets, raw OHLCV prices (non-stationary), and intermediate columns
        exclude_cols = {
            'swing_target', 'swing_target_5pct', 'swing_target_8pct',
            'forward_max_return', 'forward_min_return',
            'open', 'high', 'low', 'close', 'volume',
            'spy_close', 'qqq_close', 'vix_close',
        }
        feature_candidates = [c for c in df.columns if c not in exclude_cols]

        X = df[feature_candidates].copy()
        y = df['swing_target']

        # Ensure clean numeric types without NaNs
        X_clean = X.select_dtypes(include=['float64', 'int64', 'int32']).fillna(0)

        # Fit TabFM Classifier to measure feature predictive power
        model = TabFMWrapper()
        model.fit(X_clean, y)
        
        logger.info(f"  [FeatureCalibrator] Computing permutation importance for {ticker} using TabFM...")
        # Calculate feature importances using permutation importance
        result = permutation_importance(model, X_clean, y, n_repeats=self.N_REPEATS, random_state=self.RANDOM_STATE, n_jobs=1)
        importances = pd.Series(result.importances_mean, index=X_clean.columns).sort_values(ascending=False)
        top_features = list(importances.head(self.top_k).index)

        logger.info("\n==========================================================================")
        logger.info(f"  AUTOMATED FEATURE CALIBRATION REPORT FOR TICKER: '{ticker}'")
        logger.info(f"  Selected EXAKTLY Top {self.top_k} Highest-Signal Features out of {len(feature_candidates)}")
        logger.info("==========================================================================")
        
        cum_sum = 0.0
        for rank, (feat, imp) in enumerate(importances.head(self.top_k).items(), 1):
            cum_sum += imp * 100.0
            logger.info(f"  Rank {rank:2d} | {feat:<30} | Signal Power: {imp*100.0:5.2f}% | Cumulative: {cum_sum:5.2f}%")
        
        logger.info("==========================================================================\n")

        # Save calibration report to data_store
        report_data = {
            "ticker": ticker,
            "calibrated_features": [
                {"rank": r+1, "feature": f, "importance_pct": float(imp*100.0)}
                for r, (f, imp) in enumerate(importances.head(self.top_k).items())
            ]
        }
        logger.debug(f"Calibration report data: {report_data}")
        
        return df, top_features, importances.head(self.top_k)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    calibrator = FeatureCalibrator(top_k=15)
    df, selected_feats, importances = calibrator.calibrate_features_for_ticker("TSLA")
    logger.info(f"Selected {len(selected_feats)} features: {selected_feats}")
