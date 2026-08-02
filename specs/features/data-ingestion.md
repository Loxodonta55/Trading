# 📋 Feature Spec: Multi-Source Data Ingestion & Storage

---

## 📌 Status
- **Status**: Implemented / In Re-engineering
- **Module**: `src/data/`
- **Re-engineered Components**: `fetcher.py`, `news_fetcher.py`, `options_fetcher.py`, `sec_fetcher.py`, `sec_text_processor.py`, `political_fetcher.py`, `social_fetcher.py`, `db_manager.py`

---

## 🎯 Zweck & Funktionalität
Erfassung, Vorverarbeitung und Persistenz aller für das Swing-Predictor-Modell benötigten Datenströme. Das System kombiniert quantitative Markt-Daten mit alternativen Datenquellen (News, Optionen, SEC, Politik, Social Media).

---

## 🔄 Inkrementelle Delta-Datenaktualisierung (Mandatory Rule)

Bei jedem Neustart der Analyse wird **ausschließlich der Delta-Datensatz** (neue Handelstage seit der letzten Analyse) geladen:
1. **Letztes Update-Datum ermitteln ($T_{last}$)**: Der `MarketDataFetcher` liest das aktuellste in der Datenbank/Cache gespeicherte Datum ab.
2. **Selektiver Delta-Abruf**: Es werden nur neue Kerzen/Daten ab $T_{last} + 1\text{ Tag}$ bis heute via API angefordert.
3. **Nahtlose Fusion & UPSERT**: Neue Delta-Zeilen werden mit der bestehenden Historie zusammengeführt und mittels `INSERT OR REPLACE` in der Datenbank aktualisiert, ohne historische Daten neu herunterzuladen.

---

## 🏗️ Spezifizierte Schnittstellen & Datenströme

### 1. Markt- & Kursdaten (`fetcher.py`)
- **Quelle**: Yahoo Finance (`yfinance`) kostenfrei.
- **Daten**: OHLCV (Open, High, Low, Close, Volume) auf Tagesbasis (EOD).
- **Inkrementelles Laden**: Automatischer Abruf nur der fehlenden Tage seit $T_{last}$.

### 2. Alternative Sentiment- & Ereignisdaten
- **Options Sentiment (`options_fetcher.py`)**: Implied Volatility (IV) Skew, Put/Call Open Interest Ratio.
- **News Sentiment (`news_fetcher.py`)**: NLP Sentiment Scores (Finviz, Yahoo, AlphaVantage) inkl. 3-Tage Moving Average.
- **SEC Filings (`sec_fetcher.py`, `sec_text_processor.py`)**: Textanalyse von 10-K & 10-Q Berichten auf Risiko-Keywords und Tonalität.
- **Politische Trades (`political_fetcher.py`)**: Käufe/Verkäufe von US-Kongressabgeordneten und Senatoren.
- **Social Sentiment (`social_fetcher.py`)**: Sentiment-Scores aus X (Twitter) & Reddit.

### 3. Datenbank- & Persistenzschicht (`db_manager.py`)
- **Engine**: SQLite (`data_store/trading_data.db`)
- **Delta-Fähigkeit**: Unterstützt `INSERT OR REPLACE` (UPSERT) für alle Tabellen:
  - `market_features`: Berechnete Multimodal-Features pro Ticker und Datum.
  - `swing_predictions`: Modell-Ausgaben (`prob_up`, `prob_down`, `signal`).
  - `backtest_runs`: Metriken und Historie aller Durchläufe.
