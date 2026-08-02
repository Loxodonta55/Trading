import React from 'react';
import { Car, Search, Rocket, Cpu } from 'lucide-react';

const TICKERS = [
  { id: 'TSLA', name: 'Tesla Inc.', symbol: 'TSLA', icon: Car },
  { id: 'GOOGL', name: 'Alphabet Inc.', symbol: 'GOOGL', icon: Search },
  { id: 'SPCX', name: 'SpaceX Track', symbol: 'SPCX', icon: Rocket },
  { id: 'NVDA', name: 'NVIDIA Corp.', symbol: 'NVDA', icon: Cpu },
];

export function TickerNav({ activeTicker, onSelectTicker }) {
  return (
    <nav className="ticker-nav-bar card">
      <div className="ticker-tabs">
        {TICKERS.map((t) => {
          const IconComp = t.icon;
          const isActive = activeTicker === t.id;
          return (
            <button
              key={t.id}
              className={`ticker-tab ${isActive ? 'active' : ''}`}
              onClick={() => onSelectTicker(t.id)}
            >
              <IconComp size={18} />
              <span className="ticker-name">{t.name}</span>
              <span className="ticker-symbol">{t.symbol}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
