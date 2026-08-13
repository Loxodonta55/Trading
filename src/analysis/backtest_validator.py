import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


class BacktestValidator:
    """
    Rigorous backtest validation suite.
    Tests whether strategy performance is statistically significant
    vs. random signals, and analyzes performance across market regimes.
    """
    ANNUALIZATION_FACTOR = 252

    def __init__(self, n_simulations: int = 1000, significance_level: float = 0.95) -> None:
        """
        Initialize the validator.

        Args:
            n_simulations: Number of Monte Carlo simulations.
            significance_level: Percentile threshold for significance (e.g., 0.95 = 95th percentile).
        """
        self.n_simulations = n_simulations
        self.significance_level = significance_level

    def monte_carlo_test(self, results_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Monte Carlo significance test: shuffles trading signals N times
        and compares real strategy Sharpe against the distribution of random Sharpes.

        Args:
            results_df: Backtest results with 'signal' and 'daily_return' columns.

        Returns:
            Dict with real_sharpe, random_sharpes_mean, random_sharpes_std,
            percentile_rank, and is_significant.
        """
        logger.info(f"[BacktestValidator] Running Monte Carlo test with {self.n_simulations} simulations...")

        daily_returns = results_df['daily_return'].values
        real_signals = results_df['signal'].values

        # Real strategy Sharpe
        real_strat_returns = np.roll(real_signals, 1) * daily_returns
        real_strat_returns[0] = 0.0
        real_sharpe = self._calc_sharpe(real_strat_returns)

        # Monte Carlo: shuffle signals and compute Sharpe each time
        rng = np.random.default_rng(seed=42)
        random_sharpes = np.zeros(self.n_simulations)

        for i in range(self.n_simulations):
            shuffled_signals = rng.permutation(real_signals)
            sim_returns = np.roll(shuffled_signals, 1) * daily_returns
            sim_returns[0] = 0.0
            random_sharpes[i] = self._calc_sharpe(sim_returns)

        percentile_rank = float(np.mean(random_sharpes < real_sharpe))
        is_significant = percentile_rank >= self.significance_level

        result = {
            'real_sharpe': float(real_sharpe),
            'random_sharpes_mean': float(np.mean(random_sharpes)),
            'random_sharpes_std': float(np.std(random_sharpes)),
            'random_sharpes_95th': float(np.percentile(random_sharpes, 95)),
            'percentile_rank': percentile_rank,
            'n_simulations': self.n_simulations,
            'is_significant': is_significant
        }

        logger.info(
            f"[BacktestValidator] Monte Carlo Result: Real Sharpe={real_sharpe:.3f} | "
            f"Random Mean={result['random_sharpes_mean']:.3f} | "
            f"Percentile={percentile_rank*100:.1f}% | "
            f"Significant={'YES' if is_significant else 'NO'}"
        )
        return result

    def regime_split_analysis(self, results_df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Splits backtest performance into market regime buckets:
        Bull (20d return > 5%), Bear (20d return < -5%), Sideways.

        Args:
            results_df: Backtest results with 'close', 'strategy_return', 'daily_return' columns.

        Returns:
            Dict keyed by regime name, each containing metrics.
        """
        logger.info("[BacktestValidator] Running regime-split analysis...")

        df = results_df.copy()
        df['return_20d'] = df['close'].pct_change(20)

        regimes = {
            'bull': df['return_20d'] > 0.05,
            'bear': df['return_20d'] < -0.05,
            'sideways': (df['return_20d'] >= -0.05) & (df['return_20d'] <= 0.05)
        }

        regime_results = {}
        for regime_name, mask in regimes.items():
            regime_df = df[mask]
            if len(regime_df) < 5:
                regime_results[regime_name] = {
                    'n_days': len(regime_df),
                    'sharpe': 0.0,
                    'total_return_pct': 0.0,
                    'win_rate_pct': 0.0,
                    'note': 'Insufficient data'
                }
                continue

            strat_rets = regime_df['strategy_return']
            trade_rets = strat_rets[strat_rets != 0]

            sharpe = self._calc_sharpe(strat_rets.values)
            total_ret = float((1 + strat_rets).prod() - 1) * 100
            win_rate = float((trade_rets > 0).mean() * 100) if len(trade_rets) > 0 else 0.0
            buy_hold_ret = float((1 + regime_df['daily_return']).prod() - 1) * 100

            regime_results[regime_name] = {
                'n_days': int(len(regime_df)),
                'sharpe': float(sharpe),
                'total_return_pct': total_ret,
                'buy_hold_return_pct': buy_hold_ret,
                'win_rate_pct': win_rate,
                'n_trades': int(len(trade_rets))
            }

            logger.info(
                f"  [{regime_name.upper()}] Days={len(regime_df)} | "
                f"Sharpe={sharpe:.2f} | Return={total_ret:.1f}% | "
                f"Win Rate={win_rate:.1f}%"
            )

        return regime_results

    def full_validation_report(self, results_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Runs complete validation suite: Monte Carlo + Regime Analysis.

        Args:
            results_df: Backtest results DataFrame.

        Returns:
            Complete validation report dict.
        """
        logger.info("\n" + "=" * 60)
        logger.info("  BACKTEST VALIDATION REPORT")
        logger.info("=" * 60)

        mc_result = self.monte_carlo_test(results_df)
        regime_result = self.regime_split_analysis(results_df)

        # Overall assessment
        is_significant = mc_result['is_significant']
        bull_sharpe = regime_result.get('bull', {}).get('sharpe', 0)
        bear_sharpe = regime_result.get('bear', {}).get('sharpe', 0)
        is_regime_robust = bull_sharpe > 0 and bear_sharpe > -0.5

        report = {
            'monte_carlo': mc_result,
            'regime_analysis': regime_result,
            'overall': {
                'is_statistically_significant': is_significant,
                'is_regime_robust': is_regime_robust,
                'verdict': 'PASS' if (is_significant and is_regime_robust) else 'FAIL'
            }
        }

        logger.info(f"\n  VERDICT: {report['overall']['verdict']}")
        logger.info(f"  Statistically Significant: {'YES' if is_significant else 'NO'}")
        logger.info(f"  Regime Robust: {'YES' if is_regime_robust else 'NO'}")
        logger.info("=" * 60 + "\n")

        return report

    def _calc_sharpe(self, returns: np.ndarray) -> float:
        """Calculate annualized Sharpe ratio from daily returns array."""
        if len(returns) == 0:
            return 0.0
        mean_ret = np.mean(returns)
        std_ret = np.std(returns)
        if std_ret < 1e-9:
            return 0.0
        return float((mean_ret / std_ret) * np.sqrt(self.ANNUALIZATION_FACTOR))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Quick smoke test with synthetic data
    np.random.seed(42)
    n = 200
    test_df = pd.DataFrame({
        'close': 100 + np.cumsum(np.random.randn(n) * 0.5),
        'daily_return': np.random.randn(n) * 0.02,
        'signal': np.random.choice([-1, 0, 1], size=n, p=[0.2, 0.6, 0.2]),
        'strategy_return': np.random.randn(n) * 0.01
    })
    validator = BacktestValidator(n_simulations=100)
    report = validator.full_validation_report(test_df)
    logger.info(f"Report: {report['overall']}")
