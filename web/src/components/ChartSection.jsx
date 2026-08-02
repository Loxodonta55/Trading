import React, { useState } from 'react';
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
  const [activeTab, setActiveTab] = useState('equity'); // 'equity' | 'price'

  if (!chartData || chartData.length === 0) return null;

  const dates = chartData.map((d) => d.date);

  const equityData = {
    labels: dates,
    datasets: [
      {
        label: 'TabFM Strategy Equity',
        data: chartData.map((d) => d.equity_curve),
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.08)',
        fill: true,
        borderWidth: 2,
        tension: 0.2,
        pointRadius: 0,
      },
      {
        label: `${ticker} Buy & Hold`,
        data: chartData.map((d) => d.buy_hold_equity),
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
        label: `${ticker} Close Price ($)`,
        data: chartData.map((d) => d.close),
        borderColor: '#06B6D4',
        borderWidth: 2,
        fill: false,
        pointRadius: 0,
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
      <div className="panel-header">
        <h2>{ticker} Performance & TabFM Prediction Visualisierung</h2>
        <div className="tab-controls">
          <button
            className={`tab-btn ${activeTab === 'equity' ? 'active' : ''}`}
            onClick={() => setActiveTab('equity')}
          >
            Equity Curve
          </button>
          <button
            className={`tab-btn ${activeTab === 'price' ? 'active' : ''}`}
            onClick={() => setActiveTab('price')}
          >
            Kursverlauf & Signale
          </button>
        </div>
      </div>
      <div className="chart-wrapper">
        <Line data={activeTab === 'equity' ? equityData : priceData} options={chartOptions} />
      </div>
    </section>
  );
}
