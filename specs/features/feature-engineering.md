# 📋 Feature Spec: Multimodal Feature Engineering & Calibration

---

## 📌 Status
- **Status**: Implemented & Hardened (Phase 1 & Phase 2 Enhanced)
- **Module**: `src/features/`
- **Core Components**: `builder.py`, `calibrator.py`, `src/data/political_fetcher.py`

---

## 🎯 Zweck & Funktionalität
Transformation von Rohdaten in ein tabuläres Dataset, das für das **Google TabFM Foundation Model** und Baseline-Klassifikatoren optimiert ist. Das Modul berechnet Target-Variablen (Swing-Wendepunkte), filtert nicht-stationäre Rohpreise aus, verhindert Lookahead-Bias und kalibriert Modell-Wahrscheinlichkeiten.

---

## 🏗️ Spezifizierte Komponenten & Regeln

### 1. Feature Builder (`builder.py`)
- **Ziel-Definition (`swing_target`)**:
  - Binäres/Multiclass-Ziel: $1$ bzw. $2$ bei positivem Swing (Kursanstieg um $\ge 5\%$ bzw. $\ge 8\%$ innerhalb von 5 Tagen), sonst $0$.
- **Feature-Gruppen**:
  - *Technische Indikatoren*: RSI-14, MA-Abstände (EMA 21, EMA 50), ATR-14, Bollinger Width, Realized Volatility 20D.
  - *Cross-Asset & Divergenz-Features (Neu)*:
    - `tsla_spy_momentum_gap`: 5-Tages Momentum-Differenz Aktie vs. SPY ($R_{\text{Aktie}, 5d} - R_{\text{SPY}, 5d}$).
    - `tsla_spy_momentum_gap_10d`: 10-Tages Momentum-Differenz Aktie vs. SPY.
    - `stock_vix_divergence`: Gleichzeitiger Anstieg von Kurs und VIX als Volatilitäts-Warnsignal ($R_{\text{Aktie}, 5d} + \Delta\text{VIX}_{5d}$).
    - `vix_regime`: Binäres Regime-Flag ($\text{VIX} > \text{SMA}_{20}(\text{VIX})$).
  - *Derivate & Optionen*: Put/Call Ratio, Put/Call OI Ratio, IV Skew.
  - *Sentiment & Text*: News Sentiment (3D MA), X-Sentiment (5D Mom), SEC Text Scores.
  - *Politik & Insider (Lookahead-sicher)*: US-Kongress Trades mit Offenlegungsdatum (`disclosure_date`).
- **Normalisierung & Feature Matrix**:
  - Ausrichtung aller Datenströme auf einen einheitlichen Tages-Index.
  - Trainingsfenster: `TRAIN_WINDOW_DAYS = 120` (erhöht von 60 für robustes Sample-to-Feature-Verhältnis).

---

### 2. Feature-Selektion & Leakage-Schutz (`calibrator.py`)
- **Strikter Ausschluss von Rohkursen (Non-Stationarity & Data-Leakage Schutz)**:
  - Rohdaten (`open`, `high`, `low`, `close`, `volume`, `spy_close`, `qqq_close`, `vix_close`) werden explizit aus dem Feature-Kandidatenpool ausgeschlossen.
  - Es werden ausschließlich stationäre Kennzahlen (Renditen, Oszillatoren, Ratios, Divergenzen) als Input genutzt.
- **Signal-Power-Kalibrierung**:
  - Permutation Feature Importance über TabFM / Ensemble.
  - Automatische Selektion der Top-$K$ (z. B. Top 15) prädiktivsten Features.

---

### 3. Lookahead-Bias Prävention (`political_fetcher.py`)
- **Regel**: Politische Trades dürfen **niemals** zum `transaction_date` in die Feature-Matrix eingehen, da die Meldepflicht (STOCK Act) eine Verzögerung von bis zu 45 Tagen erlaubt.
- **Implementierung**:
  ```python
  t_date = pd.to_datetime(row.get('disclosure_date', row.get('transaction_date')))
  ```
- **Signal-Skalierung**:
  - Keine harte Abschneidung auf $[-1, 1]$, sondern Perzentil-Normalisierung zur Beibehaltung der Ordergröße:
  ```python
  max_abs_signal = df['signal'].abs().quantile(0.99) + 1e-9
  df['political_trade_signal'] = df['signal'] / max_abs_signal
  ```
