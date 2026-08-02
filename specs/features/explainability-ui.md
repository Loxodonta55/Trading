# 📋 Feature Spec & Reverse Engineering: Signal Explainability & React Dashboard SPA (FDD Spec)

---

## 📌 Feature Overview & Status
- **Feature Name**: Signal Explainability & Interactive Trading Dashboard SPA
- **Status**: Production / Active (V2.0 React SPA)
- **Module**: `web/` (React SPA) & `web/server.py` (FastAPI REST Backend)
- **Methodology**: Feature-Driven Development (FDD) & Spec-Driven Development (SDD)
- **Primary Goal**: Bereitstellung eines hochperformanten, ästhetischen und transparanten Dashboards für den Anwender, welches KI-generierte Swing-Trading-Signale (Google TabFM) in menschlich verständliche Erklärungen, visualisierte Metriken und Live-Markt-Nachrichten übersetzt.

---

## 📐 1. Reverse-Engineered UI Wireframe & Visual Hierarchy

```
+---------------------------------------------------------------------------------------------------+
| 🚀 TabFM Trading Dashboard [V2.0 React SPA]      🟢 Server Live      [ ⚡ Analyse-Pipeline ausführen ] |
+---------------------------------------------------------------------------------------------------+
| [ ⚡ TSLA Tesla Inc. ]   [ 🏢 GOOGL Alphabet ]   [ 📈 SPCX S&P 500 ]                              |
+---------------------------------------------------------------------------------------------------+
| ⚡ AKTUELLE KI-EMPFEHLUNG FÜR TSLA (2026-07-27)              🛡️ Backtest Trefferquote: 64.2% ✓    |
| +-----------------------------------------------+-----------------------------------------------+ |
| | PROGNOSTIZIERTES SIGNAL                       | KI-Konfidenz P(Up): 64%                       | |
| | 🚀 BUY SWING                                  | [======================--------] 64%          | |
| | Ziel: +5.0% Swing Gewinn                      | Aktueller Kurs: $248.50                       | |
| +-----------------------------------------------+-----------------------------------------------+ |
| | 💬 Begründung: "Das KI-Modell identifiziert ein starkes bullisches Swing-Signal für TSLA mit   | |
| |    einer Vorhersagewahrscheinlichk. von 64%. Begründet durch: überverkauftem RSI (31.2),     | |
| |    positivem News-Sentiment (0.42), bullischem Optionen-Skew (-0.18)..."                      | |
| +-----------------------------------------------------------------------------------------------+ |
| | [🎯 Ziel: +5.0%] [P(Up): 64%] [RSI: 31.2] [News: +0.42] [IV Skew: -0.18] [🏛️ US-Kongress: BUY] | |
+---------------------------------------------------------------------------------------------------+
| ✨ HEUTIGE ENTSCHEIDUNGS-KPIS FÜR TSLA (2026-07-27)                                               |
| +------------+------------+------------+------------+------------+------------+                   |
| | 1. Signal  | 2. P(Up)   | 3. RSI(14) | 4. News    | 5. IV Skew | 6. Kongress|                   |
| | BUY SWING  |    64%     |    31.2    |   +0.42    |   -0.18    |   BUY 🏛️   |                   |
| +------------+------------+------------+------------+------------+------------+                   |
| 🌐 MARKT-KATALYSATOR: "Tesla Stock Erases Year of Gains as Investors..." | Quelle: Barron's ↗     |
+---------------------------------------------------------------------------------------------------+
| +---------------------------------------------------+-------------------------------------------+ |
| | 📈 CHAKTS (TradingView / Lightweight Charts)      | 🧪 ABLATION-STUDIE (Feature Relevanz)     | |
| | [ Preis- & Signal-Visualisierung über Zeit ]      | [ Tabelle: Modell mit/ohne Features ]    | |
+---------------------------------------------------+-------------------------------------------+ |
| 📊 HISTORISCHE BACKTEST OVERVIEW & KPI BENCHMARKS                                                |
+---------------------------------------------------------------------------------------------------+
| 📜 DAY2DAY HISTORY & PREDICTION ACCURACY LOG (Signale-Tabelle)                                    |
+---------------------------------------------------------------------------------------------------+
```

---

## 🏗️ 2. Komponenten-Architektur & Responsibilities (FDD Breakdown)

### 2.1 Central Application Host (`web/src/App.jsx`)
- **Verantwortung**: Haupt-Orchestrierung von State, API-Kommunikation, Fehler-Handling und Fallback-Routing.
- **State Management**:
  - `data`: Aggregierte Dashboard-Daten (Signale, Charts, Ablation, Zusammenfassung).
  - `activeTicker`: Aktuell ausgewählter Asset-Ticker (`'TSLA'` | `'GOOGL'` | `'SPCX'`).
  - `isLoading`: Boolean für Ladezustände bei Erstaufruf & Pipeline-Ausführung.
  - `error`: String für Fehlerzustände bei Netzwerk- oder Serverproblemen.
- **Resilience / Fallback Protocol**:
  - Primär: API-Aufruf an `/api/dashboard-data`.
  - Fallback bei API-Ausfall: Lokaler Fetch von `/backtest_dashboard_data.json`.

---

### 2.2 Top Header (`web/src/components/Header.jsx`)
- **Props**: `{ onRunPipeline: () => Promise<void>, isLoading: boolean }`
- **UI Element Specs**:
  - Titel mit Gradient-Typografie & SPA-Badge (V2.0 React SPA).
  - Statischer Server-Status-Indicator (`🟢 Server Live` mit CSS Pulse-Animation).
  - Primary Action Button `Analyse-Pipeline ausführen` mit Spinner-State während `isLoading = true`.

---

### 2.3 Ticker Navigation (`web/src/components/TickerNav.jsx`)
- **Props**: `{ activeTicker: string, onSelectTicker: (symbol: string) => void }`
- **Asset Configs**:
  - `TSLA` (Tesla Inc.)
  - `GOOGL` (Alphabet Inc.)
  - `SPCX` (S&P 500 ETF)
- **UI / UX Spec**: Tabs mit aktiver Glow-Umrandung (`.ticker-tab.active`), Icon-Belegungen und Hover-Animationen.

---

### 2.4 Hero Signal Explainability Card (`web/src/components/ExplainabilityCard.jsx`)
- **Props**: `{ latestSignal: SignalObject, bestExperimentData: ExperimentObject, ticker: string }`
- **Logik & Regelbasierte Begründungs-Engine (`generateReasoningMessage()`)**:
  - Evaluierung technischer Parameter:
    - `rsi_14 < 40`: Addiert *"überverkauftem RSI (Value)"*
    - `rsi_14 > 60`: Addiert *"starkem RSI Momentum (Value)"*
    - `news_sentiment > 0.1`: Addiert *"positivem News-Sentiment (Value)"*
    - `options_iv_skew < 0`: Addiert *"bullischem Optionen-Skews (Value)"*
    - `political_trade_signal === 1`: Addiert *"positiven US-Kongress Insider-Käufen"*
  - Bei leerem Faktoren-Set: Fallback auf *"Google TabFM Zeitreihen-Musteranalyse und Relativstärke vs. SPY"*.
- **Signal-Klassifizierung**:
  - `signal === 1` $\rightarrow$ `BUY SWING 🚀` (Grüne Styling-Klasse `recommendation-buy`)
  - `signal === -1` $\rightarrow$ `TAKE PROFIT 📉` (Rote Styling-Klasse `recommendation-sell`)
  - `signal === 0` $\rightarrow$ `HOLD / WATCH 👁️` (Goldene Styling-Klasse `recommendation-hold`)
- **Meter Fill Gauge**: Dynamische Breite (`width: ${confidence}%`) für KI-Konfidenz.

---

### 2.5 Metrics & Market News Overview (`web/src/components/MetricsOverview.jsx`)
- **Props**: `{ latestSignal: SignalObject, ticker: string }`
- **Internal State**: `newsList` (Array), `isNewsLoading` (Boolean).
- **Live News Integration Lifecycle**:
  - Triggert `useEffect` bei `ticker`-Wechsel.
  - Lädt Nachrichten von Endpunkt `/api/news/${ticker}`.
  - Wenn Nachrichten geladen werden: Zeigt den aktuellsten Artikel (Titel, Provider, Publikationsdatum, Link).
  - Fallback-System: Integriertes Wörterbuch `fallbackNews` für Offline-/Dev-Betrieb.
- **KPI-Karten Grid**:
  1. *Signal für Heute*: Status & Kurs.
  2. *KI-Konfidenz $P(\text{Up})$*: Trefferwahrscheinlichkeit in Prozent.
  3. *RSI (14)*: Relativer Stärke Index mit Status ("Überverkauft", "Überkauft", "Neutral").
  4. *News Sentiment (3D MA)*: Nachrichten-Stimmungs-Score.
  5. *Options IV Skew*: Implizite Volatilitäts-Asymmetrie.
  6. *US-Kongress Trades*: Insider-Meldungen aus der US-Politik.

---

### 2.6 Interactive Price Chart Section (`web/src/components/ChartSection.jsx`)
- **Props**: `{ chartData: Array<PricePoint>, ticker: string }`
- **Technischer Stack**: Integration von TradingView `lightweight-charts` (Canvas-basiert) mit Fallback auf responsive SVG-Darstellung.
- **Visuals**: Kerzen- oder Linienchart mit farbcodierten Einstiegs- und Verkaufspunkten.

---

### 2.7 Ablation Study Table (`web/src/components/AblationTable.jsx`)
- **Props**: `{ summary: Array<ExperimentSummary>, bestExperiment: string }`
- **Zweck**: Transparenz über den Beitrag einzelner Feature-Gruppen (z. B. Modell-Performance mit vs. ohne Politic Trades / News).
- **UI Highlight**: Hervorhebung der Zeile mit dem `best_experiment` (`.highlight-row`).

---

### 2.8 Backtest Performance Overview (`web/src/components/BacktestPerformanceOverview.jsx`)
- **Props**: `{ bestExperimentData: ExperimentObject, ticker: string }`
- **KPI-Anzeige**: Total Return %, Annualized Return %, Win Rate %, Profit Factor, Max Drawdown %, Sharpe Ratio.

---

### 2.9 Signals Log (`web/src/components/SignalsLog.jsx`)
- **Props**: `{ chartData: Array<PricePoint> }`
- **Funktionalität**: Scrollbare Tabelle aller historischen Tage inklusive Datum, Schlusspreis, Signal, $P(\text{Up})$, $P(\text{Down})$, News Sentiment und Kongress-Trade-Flags.

---

## 🔄 3. Data Contracts & Interfaces (TypeScript Definitions)

```typescript
export interface SignalPoint {
  date: string;
  close: number;
  signal: -1 | 0 | 1; // -1: Sell/TakeProfit, 0: Hold, 1: Buy
  prob_up: number; // e.g. 0.64 (64%)
  prob_down: number; // e.g. 0.36 (36%)
  rsi_14: number;
  news_sentiment: number;
  news_sentiment_3d_ma: number;
  options_iv_skew: number;
  political_trade_signal: 0 | 1;
}

export interface ExperimentSummary {
  experiment: string;
  win_rate: number; // e.g. 0.642
  total_return: number; // e.g. 0.354
  max_drawdown: number; // e.g. -0.121
  sharpe_ratio?: number;
}

export interface TickerData {
  summary: ExperimentSummary[];
  best_experiment: string;
  tsla_chart_data: SignalPoint[];
}

export interface NewsItem {
  title: string;
  provider: string;
  pubDate: string;
  url: string;
}

export interface DashboardResponse {
  status: string;
  best_experiment: string;
  data: Record<string, TickerData>;
  summary: ExperimentSummary[];
  tsla_chart_data: SignalPoint[];
}
```

---

## 🎨 4. Design System & CSS Specs (`web/src/styles.css`)

### 4.1 Farbpalette & Tokens
```css
:root {
  --bg-dark: #0b0e14;
  --card-bg: #151924;
  --card-border: rgba(255, 255, 255, 0.08);
  --text-primary: #ffffff;
  --text-secondary: #90a4ae;
  
  /* Signal Colors */
  --green-up: #00e676;
  --red-down: #ff5252;
  --gold-hold: #ffd600;
  --accent-blue: #2962ff;
}
```

### 4.2 Card Styling & Glassmorphism
- **Background**: Dark Navy Slate (`#151924`) mit 8px Border Radius.
- **Borders**: Subtile semi-transparente Ränder (`rgba(255, 255, 255, 0.08)`).
- **Hero-Karten Glow**:
  - `BUY`: Linear Gradient & Green Shadow (`box-shadow: 0 8px 24px rgba(0, 230, 118, 0.15)`).
  - `SELL`: Red Shadow (`box-shadow: 0 8px 24px rgba(255, 82, 82, 0.15)`).
  - `HOLD`: Gold Shadow (`box-shadow: 0 8px 24px rgba(255, 214, 0, 0.15)`).

---

## 🧪 5. Acceptance Criteria & Test Scenarios (FDD Gherkin Spec)

### Feature: Signal Explainability Display
```gherkin
Scenario: Displaying a Bullish Swing Recommendation
  Given the latest signal for "TSLA" has signal = 1 and prob_up = 0.64
  And rsi_14 is 31.2 and political_trade_signal is 1
  When the user views the ExplainabilityCard
  Then the signal title should display "BUY SWING 🚀" in green
  And the confidence meter should fill to 64%
  And the reasoning text should mention "überverkauftem RSI (31.2)" and "US-Kongress Insider-Käufen"

Scenario: Ticker Navigation Switching
  Given the user is on the dashboard with "TSLA" selected
  When the user clicks on the "GOOGL" tab in TickerNav
  Then activeTicker state updates to "GOOGL"
  And the ExplainabilityCard, MetricsOverview and Charts refresh with GOOGL data
  And a GET request is sent to "/api/news/GOOGL"
```
