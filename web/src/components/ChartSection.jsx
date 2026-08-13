import React, { useState, useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export function ChartSection({ chartData, ticker }) {
  const [activeTab, setActiveTab] = useState('price'); // default to 'price' so users see stock chart immediately
  const [timeframe, setTimeframe] = useState('ALL'); // '1M' | '3M' | '6M' | 'YTD' | 'ALL'

  if (!chartData || chartData.length === 0) return null;

  // Filter data according to selected timeframe
  const filteredData = useMemo(() => {
    if (!chartData || chartData.length === 0) return [];
    if (timeframe === 'ALL') return chartData;

    const lastDate = new Date(chartData[chartData.length - 1].date);
    let cutoff = new Date(lastDate);

    if (timeframe === '1M') {
      cutoff.setDate(cutoff.getDate() - 30);
    } else if (timeframe === '3M') {
      cutoff.setDate(cutoff.getDate() - 90);
    } else if (timeframe === '6M') {
      cutoff.setDate(cutoff.getDate() - 180);
    } else if (timeframe === 'YTD') {
      cutoff = new Date(lastDate.getFullYear(), 0, 1);
    }

    const res = chartData.filter((d) => new Date(d.date) >= cutoff);
    return res.length > 0 ? res : chartData;
  }, [chartData, timeframe]);

  const dates = filteredData.map((d) => d.date);
  const firstDate = filteredData[0]?.date;
  const lastDate = filteredData[filteredData.length - 1]?.date;

  // Calculate signal points for price chart
  const pointRadii = filteredData.map((d) => (d.signal !== 0 ? 5 : 0));
  const pointColors = filteredData.map((d) =>
    d.signal === 1 ? '#10B981' : d.signal === -1 ? '#EF4444' : 'transparent'
  );

  const equityData = {
    labels: dates,
    datasets: [
      {
        label: 'TabFM Strategy Equity',
        data: filteredData.map((d) => d.equity_curve),
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.08)',
        fill: true,
        borderWidth: 2,
        tension: 0.2,
        pointRadius: 0,
      },
      {
        label: `${ticker} Buy & Hold`,
        data: filteredData.map((d) => d.buy_hold_equity),
        borderColor: '#6B7280',
        borderDash: [5, 5],
        borderWidth: 1.5,
        fill: false,
        pointRadius: 0,
      },
    ],
  };

  const priceData = {
    labels: dates,
    datasets: [
      {
        label: `${ticker} Kurs ($)`,
        data: filteredData.map((d) => d.close),
        borderColor: '#06B6D4',
        borderWidth: 2,
        fill: false,
        pointRadius: pointRadii,
        pointBackgroundColor: pointColors,
        pointBorderColor: pointColors,
        pointHoverRadius: 7,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#9CA3AF',
          font: { family: 'Outfit', size: 12 },
        },
      },
      tooltip: {
        backgroundColor: '#111827',
        titleColor: '#F9FAFB',
        bodyColor: '#9CA3AF',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        callbacks: {
          afterLabel: function (context) {
            const dataIndex = context.dataIndex;
            const item = filteredData[dataIndex];
            if (!item) return '';
            if (item.signal === 1) return '🚀 TabFM Signal: BUY (+5% Ziel)';
            if (item.signal === -1) return '📉 TabFM Signal: TAKE PROFIT';
            return '👁️ TabFM: HOLD (Neutral)';
          },
        },
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(255, 255, 255, 0.03)' },
        ticks: { color: '#6B7280', font: { family: 'JetBrains Mono', size: 10 } },
      },
      y: {
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: '#9CA3AF', font: { family: 'JetBrains Mono', size: 11 } },
      },
    },
  };

  return (
    <section className="chart-panel card">
      <div className="panel-header" style={{ flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2>{ticker} Performance & TabFM Prediction Visualisierung</h2>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
            Datenbereich: <strong>{firstDate}</strong> bis <strong>{lastDate}</strong> ({filteredData.length} Handelstage)
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          {/* Timeframe Controls */}
          <div className="tab-controls" style={{ background: 'rgba(255,255,255,0.03)', padding: '2px' }}>
            {['1M', '3M', '6M', 'YTD', 'ALL'].map((tf) => (
              <button
                key={tf}
                className={`tab-btn ${timeframe === tf ? 'active' : ''}`}
                style={{ padding: '4px 10px', fontSize: '12px' }}
                onClick={() => setTimeframe(tf)}
              >
                {tf}
              </button>
            ))}
          </div>

          {/* Type Controls */}
          <div className="tab-controls">
            <button
              className={`tab-btn ${activeTab === 'price' ? 'active' : ''}`}
              onClick={() => setActiveTab('price')}
            >
              Kursverlauf & Signale
            </button>
            <button
              className={`tab-btn ${activeTab === 'equity' ? 'active' : ''}`}
              onClick={() => setActiveTab('equity')}
            >
              Equity Curve
            </button>
          </div>
        </div>
      </div>
      <div className="chart-wrapper">
        <Line data={activeTab === 'equity' ? equityData : priceData} options={chartOptions} />
      </div>
    </section>
  );
}
