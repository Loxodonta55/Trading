import React from 'react';
import { BarChart2 } from 'lucide-react';

export function BacktestPerformanceOverview({ bestExperimentData, ticker }) {
  if (!bestExperimentData) return null;

  const rawReturn = bestExperimentData.total_return || 0;
  const returnPct = Math.abs(rawReturn) > 1 ? rawReturn : rawReturn * 100;
  const rawBuyHold = bestExperimentData.buy_hold_return || 0;
  const buyHoldPct = Math.abs(rawBuyHold) > 1 ? rawBuyHold : rawBuyHold * 100;
  const outperformance = returnPct - buyHoldPct;
  const rawWinRate = bestExperimentData.win_rate || 0;
  const winRatePct = rawWinRate > 1 ? rawWinRate : rawWinRate * 100;
  const trades = bestExperimentData.n_trades || bestExperimentData.num_trades || 0;
  const sharpe = (bestExperimentData.sharpe_ratio || 0).toFixed(2);
  const profitFactor = (bestExperimentData.profit_factor || 0).toFixed(2);
  const rawMaxDd = bestExperimentData.max_drawdown || 0;
  const maxDdPct = Math.abs(rawMaxDd) > 1 ? rawMaxDd : rawMaxDd * 100;

  return (
    <section className="backtest-overview-section card">
      <div className="panel-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <BarChart2 size={22} color="#10B981" />
          <h2>Historische Backtest Performance KPIs ({ticker})</h2>
        </div>
        <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
          Strategie: <strong>{bestExperimentData.experiment || 'TabFM Standard'}</strong>
        </div>
      </div>

      <div className="metrics-grid">
        <div className="card metric-card">
          <div className="metric-label">TabFM Net Return (nach Gebühren)</div>
          <div className={`metric-value ${returnPct >= 0 ? 'positive' : 'negative'}`}>
            {returnPct >= 0 ? `+${returnPct.toFixed(1)}%` : `${returnPct.toFixed(1)}%`}
          </div>
          <div className="metric-sub">
            Outperformance: {outperformance >= 0 ? `+${outperformance.toFixed(1)}%` : `${outperformance.toFixed(1)}%`}
          </div>
        </div>

        <div className="card metric-card">
          <div className="metric-label">{ticker} Buy & Hold Return</div>
          <div className={`metric-value ${buyHoldPct >= 0 ? 'positive' : 'negative'}`}>
            {buyHoldPct >= 0 ? `+${buyHoldPct.toFixed(1)}%` : `${buyHoldPct.toFixed(1)}%`}
          </div>
          <div className="metric-sub">Passiver Markt Benchmark</div>
        </div>

        <div className="card metric-card">
          <div className="metric-label">Historische Trefferquote</div>
          <div className="metric-value gold">{winRatePct.toFixed(1)}%</div>
          <div className="metric-sub">{trades} Signale im Backtest</div>
        </div>

        <div className="card metric-card">
          <div className="metric-label">Sharpe Ratio</div>
          <div className="metric-value">{sharpe}</div>
          <div className="metric-sub">Risikobereinigte Rendite</div>
        </div>

        <div className="card metric-card">
          <div className="metric-label">Profit Factor</div>
          <div className="metric-value">{profitFactor}</div>
          <div className="metric-sub">Gross Win / Loss Ratio</div>
        </div>

        <div className="card metric-card">
          <div className="metric-label">Max Drawdown</div>
          <div className="metric-value negative">-{Math.abs(maxDdPct).toFixed(1)}%</div>
          <div className="metric-sub">Peak-to-Trough Risiko</div>
        </div>
      </div>
    </section>
  );
}
