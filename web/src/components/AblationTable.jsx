import React from 'react';

export function AblationTable({ summary, bestExperiment }) {
  if (!summary || summary.length === 0) return null;

  return (
    <section className="ablation-panel card">
      <div className="panel-header">
        <h2>Multi-Source Sensitivity & Ablation Proof</h2>
        <span className="status-chip">Wissenschaftlicher Nachweis</span>
      </div>
      <p style={{ fontSize: '13px', color: '#9CA3AF', marginBottom: '16px' }}>
        Vergleich der Datenkanäle: Technische Indikatoren, Makro, News-Sentiment, US-Kongress Trades und X-Sentiment.
      </p>
      <div className="table-responsive">
        <table className="ablation-table">
          <thead>
            <tr>
              <th>Strategie</th>
              <th>Sharpe</th>
              <th>Win Rate</th>
              <th>Net Return</th>
              <th>Max DD</th>
            </tr>
          </thead>
          <tbody>
            {summary.map((row, idx) => {
              const isBest = row.experiment === bestExperiment;
              const rawWin = row.win_rate || 0;
              const winRate = (rawWin > 1 ? rawWin : rawWin * 100).toFixed(1);
              const rawRet = row.total_return || 0;
              const retPct = (Math.abs(rawRet) > 1 ? rawRet : rawRet * 100).toFixed(1);
              const rawDd = row.max_drawdown || 0;
              const maxDd = (Math.abs(rawDd) > 1 ? rawDd : rawDd * 100).toFixed(1);

              return (
                <tr key={idx} className={isBest ? 'best-row' : ''}>
                  <td>
                    {row.experiment} {isBest ? '🏆 (Optimal)' : ''}
                  </td>
                  <td>{(row.sharpe_ratio || 0).toFixed(2)}</td>
                  <td style={{ color: winRate >= 60 ? '#10B981' : '#F59E0B' }}>
                    {winRate}%
                  </td>
                  <td style={{ color: retPct >= 0 ? '#10B981' : '#EF4444' }}>
                    {retPct >= 0 ? `+${retPct}%` : `${retPct}%`}
                  </td>
                  <td style={{ color: '#EF4444' }}>-{Math.abs(maxDd)}%</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
