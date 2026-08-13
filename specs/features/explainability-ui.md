# 📋 Feature Spec & Architecture: Signal Explainability & React Dashboard SPA

---

## 📌 Feature Overview & Status
- **Feature Name**: Signal Explainability & Interactive Trading Dashboard SPA
- **Status**: Production / Active (V2.1 React SPA)
- **Module**: `web/` (React SPA) & `web/server.py` (FastAPI REST Backend)
- **Methodology**: Feature-Driven Development (FDD) & Spec-Driven Development (SDD)
- **Primary Goal**: Bereitstellung eines hochperformanten, transparenten und lückenlosen Dashboards, welches KI-generierte Swing-Trading-Signale (Google TabFM) in menschlich verständliche Erklärungen, visualisierte Metriken, zoomfähige Charts und eine vollständige Day2Day Historie übersetzt.

---

## 📐 1. Visual Hierarchy & Wireframe

```
+---------------------------------------------------------------------------------------------------+
| 🚀 TabFM Trading Dashboard [V2.1 React SPA]      🟢 Server Live      [ ⚡ Analyse-Pipeline ausführen ] |
+---------------------------------------------------------------------------------------------------+
| [ ⚡ TSLA Tesla Inc. ]   [ 🏢 GOOGL Alphabet ]   [ 📈 SPCX S&P 500 ]   [ 🎮 NVDA Nvidia ]         |
+---------------------------------------------------------------------------------------------------+
| ⚡ AKTUELLE KI-EMPFEHLUNG FÜR TSLA (2026-08-13)              🛡️ 3-Monats Trefferquote: 50.0% (5/5)   |
| +-----------------------------------------------+-----------------------------------------------+ |
| | PROGNOSTIZIERTES SIGNAL                       | KI-Konfidenz P(Up): 64% ℹ️                   | |
| | 🚀 BUY SWING                                  | [======================--------] 64%          | |
| | Ziel: +5.0% Swing Gewinn                      | Aktueller Kurs: $339.96                       | |
| +-----------------------------------------------+-----------------------------------------------+ |
| | 💬 Begründung: "Das KI-Modell identifiziert ein bullisches Swing-Signal für TSLA..."          | |
| +-----------------------------------------------------------------------------------------------+ |
| | [🎯 Ziel: +5.0%] [P(Up): 64% ℹ️] [RSI: 48.2 ℹ️] [News: +0.22 ℹ️] [IV Skew: -0.15 ℹ️]             | |
+---------------------------------------------------------------------------------------------------+
| 📈 KURSVERLAUF & SIGNALE (2025-01-23 bis 2026-08-13)   [ 1M | 3M | 6M | YTD | ALL ] [Kurs / Equity] |
| (Grüne Punkte 🟢 = Buy Signale | Rote Punkte 🔴 = Take Profit | Linie = Kurs)                     |
+---------------------------------------------------------------------------------------------------+
| 📊 TÄGLICHES SWING PREDICTION LOG & KI-TREFFERGENAUIGKEIT                                         |
| [ 📅 Alle 390 Tage (Lückenlos) ] [ 🎯 Nur Kauf/Verkauf Signale ] [ ✓ Treffer ] [ ✗ Fehlsignale ]   |
| (Jeder Börsentag lückenlos mit Datum, Close, Signal, Treffer-Status, RSI, News & Politik geloggt) |
+---------------------------------------------------------------------------------------------------+
```

---

## 🏗️ 2. Komponenten-Spezifikation

### 2.1 Chart Navigation & Timeframe Controls (`ChartSection.jsx`)
- **Timeframe Selector**:
  - `1M`: Letzte 30 Tage – Fokus auf aktuelle Tageskerzen ohne Beschriftungs-Überlagerung.
  - `3M`: Letzte 90 Tage – Kurzfristiger Swing-Kontext.
  - `6M`: Letzte 180 Tage – Mittelfristiger Trend.
  - `YTD`: Seit Jahresbeginn.
  - `ALL`: Vollständige Historie (390+ Handelstage).
- **Signal-Marker im Kursverlauf**:
  - **Kauf-Signale (`signal === 1`)**: Als markante grüne Punkte (`#10B981`, Radius 5px) auf der Kurslinie gezeichnet.
  - **Verkaufs-Signale (`signal === -1`)**: Als rote Punkte (`#EF4444`, Radius 5px) markiert.
  - **Neutral (`signal === 0`)**: Transparenter Punkt für klare Linienführung.
- **Interaktiver Tooltip**:
  - Zeigt exaktes Datum, Kurs und KI-Aktion (`BUY (+5% Ziel)`, `TAKE PROFIT` oder `HOLD (Neutral)`).

---

### 2.2 Day2Day Prediction Log & Lückenlose Historie (`SignalsLog.jsx`)
- **Standardansicht**:
  - Standardfilter ist **`📅 Alle Tage (Lückenlos)`** (`filter === 'all'`).
  - Zeigt jeden einzelnen Handelstag in chronologischer Reihenfolge (neueste zuerst) ohne Datums-Sprünge.
  - Tage ohne aktiven Trade werden transparent als **`HOLD (Kein Signal)`** ausgewiesen.
- **Spezifische Filter-Tabs**:
  - `🎯 Nur Kauf/Verkauf Signale`: Isoliert gezielt die Handelstage mit aktiver Einstiegs-/Ausstiegs-Entscheidung.
  - `✓ Treffer`: Nur erfolgreich validierte Trades.
  - `✗ Fehlsignale`: Nicht aufgegangene Trades zur Fehleranalyse.
- **Präzisions-Banner**:
  - Dynamische Anzeige der historischen Vorhersage-Präzision in % sowie Zähler für Treffer und Fehlschläge.

---

### 2.3 Entscheidungs-KPIs & Erklärbarkeit (`ExplainabilityCard.jsx` & `MetricsOverview.jsx`)
- **Faktoren-Chips & Tooltips**:
  - $P(\text{Up Swing})$ (Google TabFM Vorhersagewahrscheinlichkeit $\ge 60\%$).
  - RSI (14) Momentum ($<40$ überverkauft, $>60$ überkauft).
  - News Sentiment (3-Tages-Durchschnitt via NLP).
  - Option IV Skew (Smart Money Call-vs-Put Prämien).
  - US-Kongress Insider Disclosures (Lookahead-bereinigt).
- **Live Datum**:
  - Anzeige des jeweils tagesaktuellen Datums der letzten Marktdaten im Titel.

---

## 🧪 3. Acceptance Criteria (FDD Gherkin Spec)

```gherkin
Scenario: Continuous Timeline in Day2Day Log
  Given the user opens the Trading Dashboard
  When the Day2Day Prediction Log renders
  Then the default tab MUST be "Alle Tage (Lückenlos)"
  And the table MUST list every consecutive trading day without skipping non-signal days

Scenario: Timeframe Selection in Charts
  Given the user selects the "1M" timeframe button on the chart panel
  Then the chart MUST filter data points to the last 30 calendar days
  And the X-axis MUST display clear daily labels for every trading day in that window
```
