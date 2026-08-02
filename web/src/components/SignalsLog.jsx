import React, { useState } from 'react';
import { CheckCircle2, XCircle, Target, Award, Filter, ArrowUpRight, ArrowDownRight } from 'lucide-react';

export function SignalsLog({ chartData }) {
  const [filter, setFilter] = useState('signals'); // default to 'signals' to highlight decision accuracy

  if (!chartData || chartData.length === 0) return null;

  // Helper to determine prediction correctness
  const getPredictionOutcome = (row) => {
    if (row.signal === 1) {
      const isCorrect = row.swing_target === 2;
      return {
        isCorrect,
        statusLabel: isCorrect ? '✓ KORREKT (+5% Ziel)' : '✗ FEHLSIGNAL',
        badgeClass: isCorrect ? 'outcome-correct-buy' : 'outcome-incorrect'
      };
    } else if (row.signal === -1) {
      const isCorrect = row.swing_target === 0;
      return {
        isCorrect,
        statusLabel: isCorrect ? '✓ KORREKT (Absicherung)' : '✗ FEHLSIGNAL',
        badgeClass: isCorrect ? 'outcome-correct-sell' : 'outcome-incorrect'
      };
    }
    return {
      isCorrect: null,
      statusLabel: '-',
      badgeClass: 'outcome-neutral'
    };
  };

  // Calculate statistics
  const signalRows = chartData.filter((d) => d.signal !== 0);
  const correctRows = signalRows.filter((d) => getPredictionOutcome(d).isCorrect === true);
  const incorrectRows = signalRows.filter((d) => getPredictionOutcome(d).isCorrect === false);
  const accuracyRate = signalRows.length > 0 ? ((correctRows.length / signalRows.length) * 100).toFixed(1) : '0.0';

  // Apply filters
  let filteredData = chartData;
  if (filter === 'signals') {
    filteredData = signalRows;
  } else if (filter === 'correct') {
    filteredData = correctRows;
  } else if (filter === 'incorrect') {
    filteredData = incorrectRows;
  }

  // Display recent signals first
  const displayData = [...filteredData].reverse();

  return (
    <section className="signals-section card">
      <div className="panel-header" style={{ flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2>Tägliches Swing Prediction Log & KI-Treffergenauigkeit</h2>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
            Day2Day Auswertung aller prognostizierten Handelssignale im Zeitverlauf
          </p>
        </div>

        <div className="tab-controls">
          <button
            className={`tab-btn ${filter === 'signals' ? 'active' : ''}`}
            onClick={() => setFilter('signals')}
          >
            Alle Signale ({signalRows.length})
          </button>
          <button
            className={`tab-btn ${filter === 'correct' ? 'active' : ''}`}
            onClick={() => setFilter('correct')}
            style={{ color: filter === 'correct' ? '#10B981' : undefined }}
          >
            ✓ Treffer ({correctRows.length})
          </button>
          <button
            className={`tab-btn ${filter === 'incorrect' ? 'active' : ''}`}
            onClick={() => setFilter('incorrect')}
            style={{ color: filter === 'incorrect' ? '#EF4444' : undefined }}
          >
            ✗ Fehlsignale ({incorrectRows.length})
          </button>
          <button
            className={`tab-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            Alle Tage ({chartData.length})
          </button>
        </div>
      </div>

      {/* Stats Summary Bar */}
      <div className="prediction-stats-bar">
        <div className="stat-pill success-glow">
          <Award size={18} color="#10B981" />
          <span>Vorhersage-Präzision: <strong>{accuracyRate}%</strong> ({correctRows.length} von {signalRows.length} Signalen korrekt)</span>
        </div>
        <div className="stat-pill">
          <CheckCircle2 size={16} color="#10B981" />
          <span>Treffer (Gewinn/Absicherung): <strong>{correctRows.length}</strong></span>
        </div>
        <div className="stat-pill">
          <XCircle size={16} color="#EF4444" />
          <span>Fehlsignale: <strong>{incorrectRows.length}</strong></span>
        </div>
      </div>

      <div className="table-responsive" style={{ maxHeight: '450px' }}>
        <table className="signals-table">
          <thead>
            <tr>
              <th>Datum</th>
              <th>Close ($)</th>
              <th>TabFM Signal</th>
              <th>KI Vorhersage Treffer</th>
              <th>P(Up Swing)</th>
              <th>P(Down)</th>
              <th>RSI (14)</th>
              <th>News (3D)</th>
              <th>US Kongress</th>
            </tr>
          </thead>
          <tbody>
            {displayData.slice(0, 150).map((row, idx) => {
              const isBuy = row.signal === 1;
              const isSell = row.signal === -1;
              const probUpPct = Math.round((row.prob_up || 0.5) * 100);
              const probDownPct = Math.round((row.prob_down || 0.5) * 100);
              const outcome = getPredictionOutcome(row);

              return (
                <tr key={idx} className={outcome.isCorrect ? 'row-correct-prediction' : ''}>
                  <td><strong>{row.date}</strong></td>
                  <td>${(row.close || 0).toFixed(2)}</td>
                  <td>
                    {isBuy ? (
                      <span className="signal-tag buy">BUY SWING 🚀</span>
                    ) : isSell ? (
                      <span className="signal-tag sell">TAKE PROFIT 📉</span>
                    ) : (
                      <span className="signal-tag hold">HOLD</span>
                    )}
                  </td>
                  <td>
                    <span className={`outcome-badge ${outcome.badgeClass}`}>
                      {outcome.statusLabel}
                    </span>
                  </td>
                  <td style={{ color: probUpPct >= 60 ? '#10B981' : '#9CA3AF', fontWeight: probUpPct >= 60 ? '700' : '400' }}>
                    {probUpPct}%
                  </td>
                  <td>{probDownPct}%</td>
                  <td>{(row.rsi_14 || 50).toFixed(1)}</td>
                  <td>{(row.news_sentiment_3d_ma || 0).toFixed(2)}</td>
                  <td>
                    {row.political_trade_signal === 1 ? (
                      <span style={{ color: '#10B981', fontWeight: 'bold' }}>BUY 🏛️</span>
                    ) : (
                      <span style={{ color: '#6B7280' }}>-</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}

