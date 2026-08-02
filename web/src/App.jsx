import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { TickerNav } from './components/TickerNav';
import { ExplainabilityCard } from './components/ExplainabilityCard';
import { MetricsOverview } from './components/MetricsOverview';
import { ChartSection } from './components/ChartSection';
import { AblationTable } from './components/AblationTable';
import { BacktestPerformanceOverview } from './components/BacktestPerformanceOverview';
import { SignalsLog } from './components/SignalsLog';

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

  const tickerData = data?.data?.[activeTicker] || null;
  const bestExpName = tickerData?.best_experiment || data?.best_experiment;
  const summary = tickerData?.summary || data?.summary || [];
  const chartData = tickerData?.tsla_chart_data || data?.tsla_chart_data || [];
  const bestExperimentData = summary.find((s) => s.experiment === bestExpName) || summary[0] || null;
  const latestSignal = chartData.length > 0 ? chartData[chartData.length - 1] : null;

  return (
    <div className="app-container">
      <Header onRunPipeline={handleRunPipeline} isLoading={isLoading} />
      
      <TickerNav activeTicker={activeTicker} onSelectTicker={setActiveTicker} />

      {error && (
        <div className="card" style={{ border: '1px solid #EF4444', color: '#EF4444' }}>
          {error}
        </div>
      )}

      {/* Top Hero: Current KI Recommendation */}
      {latestSignal && (
        <ExplainabilityCard
          latestSignal={latestSignal}
          bestExperimentData={bestExperimentData}
          ticker={activeTicker}
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
      <div className="dashboard-grid">
        <ChartSection chartData={chartData} ticker={activeTicker} />
        <AblationTable summary={summary} bestExperiment={bestExpName} />
      </div>

      {/* Historical Backtest KPIs: Moved Down to Daily Price & Backtest Section */}
      <BacktestPerformanceOverview
        bestExperimentData={bestExperimentData}
        ticker={activeTicker}
      />

      {/* Day2Day History & Prediction Accuracy Log */}
      <SignalsLog chartData={chartData} />
    </div>
  );
}
