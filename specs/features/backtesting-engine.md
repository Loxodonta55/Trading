# 📋 Feature Spec: Walk-Forward Backtester & Rigorous Validation

---

## 📌 Status
- **Status**: Implemented & Hardened (Phase 4 Validation Suite Added)
- **Module**: `src/backtest/`, `src/analysis/`
- **Core Components**: `engine.py`, `evaluator.py`, `backtest_validator.py`

---

## 🎯 Zweck & Funktionalität
Simulation realistischer Swing-Trading-Strategien mit rollierender Walk-Forward-Validierung zur Vermeidung von Overfitting. Durchführung rigoroser statistischer Signifikanz-Tests (Monte Carlo) und Regime-Split Analysen, um sicherzustellen, dass Gewinne nicht auf Zufall basieren.

---

## 🏗️ Spezifizierte Komponenten

### 1. Walk-Forward Backtester (`engine.py`)
- **Backtest-Modus**: Rollierendes Walk-Forward Fenster (`TRAIN_WINDOW_DAYS = 120`).
- **Handelsregeln & Ausführung**:
  - Einstieg bei KI-Konfidenz `prob_up >= DEFAULT_CONFIDENCE_THRESHOLD` (0.62) oder Target `prob_up >= 0.60`.
  - Risikomanagement: Fester Stop-Loss (z. B. $-2.5\%$) und Take-Profit (z. B. $+5.0\%$).
  - Berücksichtigung von Slippage und Transaktionskosten (10 bps).
- **Metriken**:
  - **Trefferquote (Win Rate)**: Ziel $\ge 60\%$.
  - **Sharpe Ratio**, **Maximum Drawdown**, **Profit Factor**, **Equity Curve vs. Buy & Hold**.

---

### 2. Statistische Validierung (`backtest_validator.py`)
- **Monte Carlo Signifikanz-Test (`monte_carlo_test`)**:
  - $N = 500 \dots 1000$ Zufalls-Simulationen (Permutation der Handelssignale).
  - Berechnung der Verteilung von Zufalls-Sharpe-Ratios.
  - Signifikanz-Kriterium: Reale Sharpe Ratio muss mindestens im **95. Perzentil** ($\ge 95\%$) der Zufallsverteilung liegen (`is_significant = True`).
- **Regime-Split Analyse (`regime_split_analysis`)**:
  - Trennung der Performance nach Marktphasen:
    - **Bull Regime**: 20-Tage Return $> +5\%$.
    - **Bear Regime**: 20-Tage Return $< -5\%$.
    - **Sideways Regime**: 20-Tage Return zwischen $-5\%$ und $+5\%$.
  - Nachweis, dass die Strategie in unterschiedlichen Marktphasen stabil agiert (`is_regime_robust = True`).
- **Gesamtverdikt**:
  - `VERDICT = PASS` nur wenn sowohl statistisch signifikant als auch regime-robust.

---

### 3. Ablations- & Benchmark-Evaluator (`evaluator.py`)
- **Vergleichsmodelle**:
  1. TabFM (Standard 5% Swing Target)
  2. TabFM (Strong 8% Swing Target)
  3. XGBoost (Standard 5% Swing Target)
  4. XGBoost (Strong 8% Swing Target)
  5. Random Forest Baseline
  6. Logistic Regression Baseline
- **Automatisierte Validierung**:
  - Nach Abschluss aller Experimente wird automatisch der `BacktestValidator` auf das bestplatzierte Modell angewendet und der vollständige Report im Log ausgegeben.
