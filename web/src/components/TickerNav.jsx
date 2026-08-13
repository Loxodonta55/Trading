import React from 'react';
import { Car, Search, Rocket, Cpu, Star } from 'lucide-react';
import { LEVERAGED_ETFS } from '../constants/leveragedEtfs';

const TICKERS = [
  { id: 'TSLA', name: 'Tesla Inc.', symbol: 'TSLA', icon: Car },
  { id: 'GOOGL', name: 'Alphabet Inc.', symbol: 'GOOGL', icon: Search },
  { id: 'SPCX', name: 'SpaceX Track', symbol: 'SPCX', icon: Rocket },
  { id: 'NVDA', name: 'NVIDIA Corp.', symbol: 'NVDA', icon: Cpu },
];

export function TickerNav({ activeTicker, onSelectTicker, tickersStatus }) {
  return (
    <nav className="ticker-nav-bar card">
      <div className="ticker-tabs">
        {TICKERS.map((t) => {
          const IconComp = t.icon;
          const isActive = activeTicker === t.id;
          const status = tickersStatus?.[t.id];
          const isJumpPending = status?.isJumpPending;
          const etfData = LEVERAGED_ETFS[t.id];
          const probUp = status ? Math.round((status.prob_up || 0) * 100) : null;

          return (
            <button
              key={t.id}
              className={`ticker-tab ${isActive ? 'active' : ''} ${isJumpPending ? 'has-jump-star' : ''}`}
              onClick={() => onSelectTicker(t.id)}
            >
              {/* Star Indicator for Jump Pending */}
              {isJumpPending && (
                <div className="tab-jump-star-badge" title="⭐ Diese Aktie steht heute vor einem prognostizierten Kurssprung (+5% Swing Up)!">
                  <Star size={16} fill="#F59E0B" color="#F59E0B" className="star-pulse" />
                  <span className="star-text">VOR SPRUNG</span>
                </div>
              )}

              <div className="tab-main-info">
                <IconComp size={18} className="tab-icon" />
                <div className="tab-text-block">
                  <div className="tab-name-row">
                    <span className="ticker-name">{t.name}</span>
                    {isJumpPending && (
                      <span className="star-inline-icon">⭐</span>
                    )}
                  </div>
                  {etfData && (
                    <div className="tab-etf-subtag">
                      IBKR Hebel: <strong>{etfData.longUS.ticker}</strong> ({etfData.longUS.leverage})
                    </div>
                  )}
                </div>
              </div>

              <div className="tab-symbol-col">
                <span className="ticker-symbol">{t.symbol}</span>
                {probUp !== null && (
                  <span className={`tab-prob-sub ${isJumpPending ? 'text-positive' : ''}`}>
                    P(Up): {probUp}%
                  </span>
                )}
              </div>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
