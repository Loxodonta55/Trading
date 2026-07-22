import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from src.features.builder import FeatureBuilder
from src.backtest.engine import WalkForwardBacktester

class SensitivityEvaluator:
    """
    Evaluates multi-source feature subsets and compares TabFM performance against 
    traditional Old School ML models (Logistic Regression, Decision Trees, Random Forests, XGBoost).
    """
    def __init__(self, confidence_threshold: float = 0.55):
        self.builder = FeatureBuilder()
        self.backtester = WalkForwardBacktester(confidence_threshold=confidence_threshold)

    def run_ablation_experiments(self) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        df = self.builder.build_dataset()
        
        # Feature Group Definitions
        tech_cols = [
            'return_1d', 'return_3d', 'return_5d', 'return_10d',
            'ema_9_ratio', 'ema_21_ratio', 'ema_50_ratio',
            'rsi_14', 'macd', 'macd_hist', 'atr_ratio',
            'bollinger_pos', 'bollinger_width', 'volume_ratio_5d'
        ]
        
        inst_cols = [c for c in ['obv_10d_pct', 'mfi_14', 'vwap_ratio_5d', 'multi_timeframe_trend'] if c in df.columns]
        opt_cols = [c for c in ['put_call_oi_ratio', 'put_call_vol_ratio', 'options_iv_skew', 'options_smart_money_bullish'] if c in df.columns]
        macro_cols = [c for c in ['spy_return_1d', 'tsla_vs_spy_rel_strength', 'vix_change_1d'] if c in df.columns]
        news_cols = [c for c in ['news_sentiment', 'press_release_flag', 'news_volume', 'news_sentiment_3d_ma'] if c in df.columns]
        sec_cols = [c for c in ['sec_filing_flag', 'sec_8k_flag', 'sec_form4_insider_flag', 'sec_10k_10q_flag', 'sec_filing_count_30d', 'days_since_last_sec_filing'] if c in df.columns]
        pol_cols = [c for c in ['political_trade_signal', 'political_net_buy_10d', 'political_disclosure_flag'] if c in df.columns]
        soc_cols = [c for c in ['x_sentiment_score', 'x_post_volume_ratio', 'x_hype_spike', 'x_sentiment_5d_mom'] if c in df.columns]

        best_features = tech_cols + macro_cols + sec_cols + opt_cols + inst_cols + news_cols

        # 1. Compare Model Architectures on the Best Feature Set
        models_to_test = {
            "1. Logistic Regression (Old School Linear)": "logistic",
            "2. Decision Tree (Old School Tree)": "decision_tree",
            "3. Random Forest (Classic Ensemble)": "random_forest",
            "4. Gradient Boosted Trees (XGBoost Baseline)": "gbm",
            "5. Google TabFM (Tabular Foundation Model)": "TabFM"
        }

        results_summary = []
        experiment_dfs = {}

        print("\n==================================================")
        print("OLD SCHOOL vs TABFM MODEL COMPARISON EXPERIMENT")
        print("==================================================")

        for exp_name, model_key in models_to_test.items():
            print(f"\n[Evaluator] Running Backtest for Architecture: {exp_name}")
            res_df, metrics = self.backtester.run_backtest(df, feature_cols=best_features, model_name=model_key)
            
            metrics['experiment'] = exp_name
            metrics['num_features'] = len(best_features)
            results_summary.append(metrics)
            experiment_dfs[exp_name] = res_df

        summary_df = pd.DataFrame(results_summary)
        cols_order = ['experiment', 'num_features', 'sharpe_ratio', 'win_rate', 'total_return', 'profit_factor', 'max_drawdown', 'n_trades']
        summary_df = summary_df[cols_order]

        print("\n==================================================")
        print("MODEL ARCHITECTURE BENCHMARK SUMMARY (OLD SCHOOL vs TABFM)")
        print("==================================================")
        print(summary_df.to_string(index=False))

        return summary_df, experiment_dfs

if __name__ == "__main__":
    evaluator = SensitivityEvaluator()
    summary, _ = evaluator.run_ablation_experiments()
