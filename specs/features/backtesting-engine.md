# 📋 Feature Spec: Walk-Forward Backtester & Ablation Evaluation

---

## 📌 Status
- **Status**: Implemented / In Re-engineering
- **Module**: `src/backtest/`, `src/analysis/`
- **Re-engineered Components**: `engine.py`, `evaluator.py`

---

## 🎯 Zweck & Funktionalität
Simulation realistischer Swing-Trading-Strategien mit Walk-Forward-Validierung zur Vermeidung von Overfitting. Evaluierung der Trefferquote (Ziel: $\ge 60\%$) und Quantifizierung der Feature-Wichtigkeit durch Ablations-Studien.

---

## 🏗️ Spezifizierte Komponenten

### 1. Walk-Forward Backtester (`engine.py`)
- **Backtest-Modus**: Walk-Forward Out-of-Sample Validierung.
- **Handelsregeln**:
  - Einstieg bei `prob_up >= Threshold` (z. B. 0.60).
  - Positionsgröße (Position Sizing) & Risikokontrolle.
  - Berücksichtigung von Slippage und Transaktionskosten.
- **Metriken**:
  - **Trefferquote (Win Rate)**: Ziel $\ge 60\%$.
  - **Sharpe Ratio**, **Maximum Drawdown**, **Profit Factor**, **Equity Curve vs. Buy & Hold**.

### 2. Ablations- & Sensitivitäts-Evaluator (`evaluator.py`)
- **Experimente**:
  - *Full Multimodal* (Technisch + Optionen + Sentiment + SEC + Politik).
  - *Technical Only* (Nur Kurs & RSI).
  - *No Sentiment* (Exklusive Social/News).
- **Ziel**: Nachweis, welche Feature-Kombination die beste Sharpe Ratio und Trefferquote liefert.
