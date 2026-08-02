# 📋 Feature Spec: Multimodal Feature Engineering & Calibration

---

## 📌 Status
- **Status**: Implemented / In Re-engineering
- **Module**: `src/features/`
- **Re-engineered Components**: `builder.py`, `calibrator.py`

---

## 🎯 Zweck & Funktionalität
Transformation von Rohdaten in ein tabuläres Dataset, das für das **Google TabFM Foundation Model** und Baseline-Klassifikatoren optimiert ist. Das Modul berechnet Target-Variablen (Swing-Wendepunkte) und kalibriert Modell-Wahrscheinlichkeiten.

---

## 🏗️ Spezifizierte Komponenten

### 1. Feature Builder (`builder.py`)
- **Ziel-Definition (`swing_target`)**:
  - Binäres oder multi-class Ziel: $1$ bei positivem Swing (Kursanstieg um $\ge X\%$ innerhalb von $N$ Tagen), sonst $0$.
- **Feature-Gruppen**:
  - *Technische Indikatoren*: RSI-14, MA-Abstände, Volatilität, Relativstärke vs. SPY.
  - *Derivate & Optionen*: Put/Call Ratio, IV Skew.
  - *Sentiment & Text*: News Sentiment, X-Sentiment, SEC Text Scores.
  - *Politik*: Kongress-Trading Signale.
- **Normalisierung & Feature Matrix**: Ausrichtung aller Datenströme auf einen einheitlichen Tages-Index ohne Lookahead-Bias.

### 2. Wahrscheinlichkeits-Kalibrierung (`calibrator.py`)
- **Verfahren**: Isotonic Regression / Platt Scaling.
- **Ziel**: Transformation von Modell-Raw-Scores in echte Gewinnwahrscheinlichkeiten ($0.0 \dots 1.0$), um Schwellenwerte (z. B. $\ge 60\%$ Wahrscheinlichkeit) präzise durchzusetzen.
