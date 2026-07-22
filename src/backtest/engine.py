import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from config import TRAIN_WINDOW_DAYS, SWING_HORIZON_DAYS, SWING_UP_THRESHOLD, SWING_DOWN_THRESHOLD
from src.models.tabfm_wrapper import TabFMWrapper
from src.models.baseline_models import BaselineClassifier

class WalkForwardBacktester:
    """
    Simulates real-world zero-shot walk-forward trading without lookahead bias.
    Trains TabFM / Baseline model on rolling historical window and evaluates swing predictions on upcoming test days.
    """
    def __init__(self, confidence_threshold: float = 0.50):
        self.confidence_threshold = confidence_threshold

    def run_backtest(
        self, 
        df: pd.DataFrame, 
        feature_cols: List[str], 
        model_name: str = "TabFM"
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        print(f"[WalkForwardBacktester] Starting walk-forward backtest for {model_name}...")
        print(f"Features included ({len(feature_cols)}): {feature_cols}")

        X = df[feature_cols]
        y = df['swing_target']
        dates = df.index
        closes = df['close'].values
        highs = df['high'].values
        lows = df['low'].values

        n_samples = len(df)
        min_train_size = min(TRAIN_WINDOW_DAYS, int(n_samples * 0.3))

        signals = np.zeros(n_samples) # 0: Cash, 1: Long, -1: Short
        probs_up = np.zeros(n_samples)
        probs_down = np.zeros(n_samples)

        # Select model instance
        if model_name.lower() == "tabfm":
            model = TabFMWrapper()
        elif "logistic" in model_name.lower():
            model = BaselineClassifier(model_type="logistic")
        elif "tree" in model_name.lower():
            model = BaselineClassifier(model_type="decision_tree")
        elif "forest" in model_name.lower():
            model = BaselineClassifier(model_type="random_forest")
        else:
            model = BaselineClassifier(model_type="gbm")

        # Import RETRAIN_EVERY_N_DAYS
        from config import RETRAIN_EVERY_N_DAYS

        # Walk-Forward Simulation Loop
        for i in range(min_train_size, n_samples):
            # Retrain model only every N days or on first iteration
            if (i - min_train_size) % RETRAIN_EVERY_N_DAYS == 0 or i == min_train_size:
                X_train = X.iloc[max(0, i - TRAIN_WINDOW_DAYS):i]
                y_train = y.iloc[max(0, i - TRAIN_WINDOW_DAYS):i]
                model.fit(X_train, y_train)

            # Predict day i
            X_test = X.iloc[i:i+1]
            p = model.predict_proba(X_test)[0]
            
            p_down, p_neutral, p_up = p[0], p[1], p[2]
            probs_down[i] = p_down
            probs_up[i] = p_up

            # Signal Generation
            if p_up >= self.confidence_threshold and p_up > p_down:
                signals[i] = 1 # Buy / Long Signal
            elif p_down >= self.confidence_threshold and p_down > p_up:
                signals[i] = -1 # Short / Sell Signal
            else:
                signals[i] = 0

        # Construct Backtest Performance Dataframe
        results_df = df.copy()
        results_df['signal'] = signals
        results_df['prob_up'] = probs_up
        results_df['prob_down'] = probs_down

        # Calculate Trading Returns & IBKR Transaction Costs
        results_df['daily_return'] = results_df['close'].pct_change(1).fillna(0.0)
        
        # Detect Trade Execution Events (Entry, Reversal, Exit)
        trade_executions = (results_df['signal'].diff() != 0) & (results_df['signal'] != 0)
        
        # Interactive Brokers Fee Structure (IBKR Pro Fixed/Tiered: $1.00 min order fee + 3 bps slippage = ~0.05% per order side)
        ibkr_cost_per_order = 0.0005 
        
        gross_strategy_return = (results_df['signal'].shift(1) * results_df['daily_return']).fillna(0.0)
        # Subtract transaction cost on execution days
        net_strategy_return = gross_strategy_return - (trade_executions.astype(float) * ibkr_cost_per_order)
        
        results_df['strategy_return'] = net_strategy_return
        results_df['equity_curve'] = (1.0 + results_df['strategy_return']).cumprod().fillna(1.0)
        results_df['buy_hold_equity'] = (1.0 + results_df['daily_return']).cumprod().fillna(1.0)

        # Compute Metrics
        metrics = self._calculate_metrics(results_df)
        metrics['model_name'] = model_name

        print(f"[WalkForwardBacktester] {model_name} Backtest Complete.")
        print(f"Total Return: {metrics['total_return']:.2f}% | Win Rate: {metrics['win_rate']:.1f}% | Sharpe Ratio: {metrics['sharpe_ratio']:.2f} | Max Drawdown: {metrics['max_drawdown']:.2f}%")

        return results_df, metrics

    def _calculate_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        returns = df['strategy_return'].iloc[TRAIN_WINDOW_DAYS:]
        equity = df['equity_curve'].iloc[TRAIN_WINDOW_DAYS:]
        
        total_return = (equity.iloc[-1] - 1.0) * 100.0 if len(equity) > 0 else 0.0
        
        trade_returns = returns[returns != 0]
        n_trades = len(trade_returns)
        wins = trade_returns[trade_returns > 0]
        losses = trade_returns[trade_returns < 0]
        
        win_rate = (len(wins) / n_trades * 100.0) if n_trades > 0 else 0.0
        gross_profit = wins.sum()
        gross_loss = abs(losses.sum())
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (gross_profit if gross_profit > 0 else 1.0)

        # Sharpe Ratio (annualized, assuming 252 trading days)
        mean_ret = returns.mean()
        std_ret = returns.std()
        sharpe = (mean_ret / (std_ret + 1e-9)) * np.sqrt(252) if std_ret > 0 else 0.0

        # Max Drawdown
        peak = equity.cummax()
        drawdown = (equity - peak) / peak
        max_dd = drawdown.min() * 100.0 if len(drawdown) > 0 else 0.0

        return {
            "total_return": total_return,
            "win_rate": win_rate,
            "n_trades": n_trades,
            "profit_factor": profit_factor,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_dd,
            "buy_hold_return": (df['buy_hold_equity'].iloc[-1] - 1.0) * 100.0
        }
