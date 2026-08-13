import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { JumpRadarBanner } from './components/JumpRadarBanner';
import { TickerNav } from './components/TickerNav';
import { ExplainabilityCard } from './components/ExplainabilityCard';
import { IbkrLeveragedEtfCard } from './components/IbkrLeveragedEtfCard';
import { MetricsOverview } from './components/MetricsOverview';
import { ChartSection } from './components/ChartSection';
import { AblationTable } from './components/AblationTable';
import { BacktestPerformanceOverview } from './components/BacktestPerformanceOverview';
import { SignalsLog } from './components/SignalsLog';

const TICKER_NAMES = {
  TSLA: 'Tesla Inc.',
  GOOGL: 'Alphabet Inc.',
  SPCX: 'SpaceX Track',
  NVDA: 'NVIDIA Corp.',
};

export default function App() {
  const [data, setData] = useState(null);
  const [activeTicker, setActiveTicker] = useState('TSLA');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const res = await fetch('/api/dashboard-data');
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      const json = await res.json();
      setData(json);
    } catch (err) {
      console.warn("API fetch failed, attempting fallback to static JSON", err);
      try {
        const res = await fetch('/backtest_dashboard_data.json');
        const json = await res.json();
        setData(json);
      } catch (fallbackErr) {
        setError("Fehler beim Laden der Dashboards-Daten. Stelle sicher, dass der Server läuft.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRunPipeline = async () => {
    try {
      setIsLoading(true);
      const res = await fetch('/api/run-analysis', { method: 'POST' });
      if (res.ok) {
        await loadData();
      } else {
        alert("Fehler beim Ausführen der Analyse-Pipeline.");
      }
    } catch (err) {
      console.error(err);
      alert("Netzwerkfehler beim Starten der Analyse.");
    } finally {
      setIsLoading(false);
    }
  };

  // Compute jump status for each of the 4 stocks (Stand heute)
  const allTickers = ['TSLA', 'GOOGL', 'SPCX', 'NVDA'];
  const tickersStatus = {};
  allTickers.forEach((sym) => {
    const tData = data?.data?.[sym];
    const tChart = tData?.chart_data || [];
    const tLatest = tChart.length > 0 ? tChart[tChart.length - 1] : null;
    const isJumpPending = tLatest ? (tLatest.signal === 1 || (tLatest.prob_up !== undefined && tLatest.prob_up >= 0.60)) : false;
    tickersStatus[sym] = {
      name: TICKER_NAMES[sym] || sym,
      date: tLatest?.date || '',
      signal: tLatest?.signal ?? 0,
      prob_up: tLatest?.prob_up ?? 0,
      close: tLatest?.close ?? 0,
      isJumpPending,
    };
  });

  const tickerData = data?.data?.[activeTicker] || null;
  const bestExpName = tickerData?.best_experiment || data?.best_experiment;
  const summary = tickerData?.summary || data?.summary || [];
  const chartData = tickerData?.chart_data || tickerData?.tsla_chart_data || data?.tsla_chart_data || [];
  const bestExperimentData = summary.find((s) => s.experiment === bestExpName) || summary[0] || null;
  const latestSignal = chartData.length > 0 ? chartData[chartData.length - 1] : null;

  return (
    <div className="app-container">
      <Header onRunPipeline={handleRunPipeline} isLoading={isLoading} />
      
      {/* 1) Dynamic Startseite Jump-Radar Banner (Kurssprung Überwachung) */}
      <JumpRadarBanner
        tickersStatus={tickersStatus}
        activeTicker={activeTicker}
        onSelectTicker={setActiveTicker}
      />

      {/* 2) Ticker Navigation with Star & Leveraged ETF Tags */}
      <TickerNav
        activeTicker={activeTicker}
        onSelectTicker={setActiveTicker}
        tickersStatus={tickersStatus}
      />

      {error && (
        <div className="card" style={{ border: '1px solid #EF4444', color: '#EF4444', padding: '16px', margin: '16px 0', textAlign: 'center' }}>
          <p style={{ fontWeight: '600', marginBottom: '8px' }}>⚠️ {error}</p>
          <button className="btn primary" onClick={loadData} style={{ marginTop: '8px' }}>
            Erneut versuchen
          </button>
        </div>
      )}

      {isLoading && !data && (
        <div className="card" style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
          <div className="spin" style={{ display: 'inline-block', width: '32px', height: '32px', border: '3px solid rgba(16, 185, 129, 0.2)', borderTopColor: '#10B981', borderRadius: '50%', marginBottom: '16px' }}></div>
          <h3>Lade Trading Dashboard Daten...</h3>
          <p style={{ fontSize: '13px', marginTop: '8px' }}>Verbinde mit TabFM Backend & lade Marktdaten...</p>
        </div>
      )}

      {/* Top Hero: Current KI Recommendation & Star Badge */}
      {latestSignal && (
        <ExplainabilityCard
          latestSignal={latestSignal}
          bestExperimentData={bestExperimentData}
          ticker={activeTicker}
          chartData={chartData}
        />
      )}

      {/* Interactive Brokers (IBKR) Leveraged ETF Order-Box (US & EU UCITS Tickers + ISINs) */}
      {latestSignal && (
        <IbkrLeveragedEtfCard
          ticker={activeTicker}
          latestSignal={latestSignal}
        />
      )}

      {/* Top KPI Boxen: EXCLUSIVELY Today's Decision KPIs & Real Verified News Line */}
      {latestSignal && (
        <MetricsOverview
          latestSignal={latestSignal}
          ticker={activeTicker}
        />
      )}

      {/* Daily Price Chart & Ablation Table */}
      {chartData.length > 0 && (
        <div className="dashboard-grid">
          <ChartSection chartData={chartData} ticker={activeTicker} />
          <AblationTable summary={summary} bestExperiment={bestExpName} />
        </div>
      )}

      {/* Historical Backtest KPIs: Moved Down to Daily Price & Backtest Section */}
      {bestExperimentData && (
        <BacktestPerformanceOverview
          bestExperimentData={bestExperimentData}
          ticker={activeTicker}
        />
      )}

      {/* Day2Day History & Prediction Accuracy Log */}
      {chartData.length > 0 && (
        <SignalsLog chartData={chartData} />
      )}
    </div>
  );
}
