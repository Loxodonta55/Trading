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
    Evaluates which multi-source feature subsets yield the best TabFM predictive performance.
    Runs feature ablation experiments across Technicals, Macro, News, Political Trades, and Social signals.
    """
    def __init__(self):
        self.builder = FeatureBuilder()
        self.backtester = WalkForwardBacktester(confidence_threshold=0.50)

    def run_ablation_experiments(self) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        df = self.builder.build_dataset()
        
        # Feature Group Definitions
        tech_cols = [
            'return_1d', 'return_3d', 'return_5d', 'return_10d',
            'ema_9_ratio', 'ema_21_ratio', 'ema_50_ratio',
            'rsi_14', 'macd', 'macd_hist', 'atr_ratio',
            'bollinger_pos', 'bollinger_width', 'volume_ratio_5d'
        ]
        
        macro_cols = [c for c in ['spy_return_1d', 'tsla_vs_spy_rel_strength', 'vix_change_1d'] if c in df.columns]
        news_cols = [c for c in ['news_sentiment', 'press_release_flag', 'news_volume', 'news_sentiment_3d_ma'] if c in df.columns]
        pol_cols = [c for c in ['political_trade_signal', 'political_net_buy_10d', 'political_disclosure_flag'] if c in df.columns]
        soc_cols = [c for c in ['x_sentiment_score', 'x_post_volume_ratio', 'x_hype_spike', 'x_sentiment_5d_mom'] if c in df.columns]

        experiments = {
            "1. Technicals Only": tech_cols,
            "2. Technicals + Market Macro": tech_cols + macro_cols,
            "3. Tech + Macro + News Sentiment": tech_cols + macro_cols + news_cols,
            "4. Tech + Macro + News + Political Trades": tech_cols + macro_cols + news_cols + pol_cols,
            "5. Full Multi-Source (All Signals)": tech_cols + macro_cols + news_cols + pol_cols + soc_cols
        }

        results_summary = []
        experiment_dfs = {}

        for exp_name, feature_subset in experiments.items():
            print(f"\n==================================================")
            print(f"Running Experiment: {exp_name}")
            print(f"==================================================")
            
            res_df, metrics = self.backtester.run_backtest(df, feature_cols=feature_subset, model_name="TabFM")
            
            metrics['experiment'] = exp_name
            metrics['num_features'] = len(feature_subset)
            results_summary.append(metrics)
            experiment_dfs[exp_name] = res_df

        summary_df = pd.DataFrame(results_summary)
        cols_order = ['experiment', 'num_features', 'sharpe_ratio', 'win_rate', 'total_return', 'profit_factor', 'max_drawdown', 'n_trades']
        summary_df = summary_df[cols_order]

        print("\n==================================================")
        print("MULTI-SOURCE FEATURE ABLATION EXPERIMENT SUMMARY")
        print("==================================================")
        print(summary_df.to_string(index=False))

        return summary_df, experiment_dfs

if __name__ == "__main__":
    evaluator = SensitivityEvaluator()
    summary, _ = evaluator.run_ablation_experiments()
