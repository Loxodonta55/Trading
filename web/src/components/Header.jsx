import React from 'react';
import { RefreshCw, ShieldCheck } from 'lucide-react';

export function Header({ onRunPipeline, isLoading }) {
  return (
    <header className="app-header">
      <div className="logo-area">
        <div className="logo-badge">TabFM</div>
        <div>
          <h1>Trading Swing Predictor (React SPA)</h1>
          <p className="subtitle">Spec-Driven Development Architecture | Multi-Source Google TabFM Engine</p>
        </div>
      </div>
      <div className="header-actions">
        <span className="status-chip live">
          <span className="pulse"></span> TabFM 2026 Engine Active
        </span>
        <span className="status-chip">
          <ShieldCheck size={14} color="#10B981" /> IBKR Pro Fees ($1.00 + 3bps)
        </span>
        <button className="btn primary" onClick={onRunPipeline} disabled={isLoading}>
          <RefreshCw size={16} className={isLoading ? "spin" : ""} />
          <span>{isLoading ? "Berechne..." : "Analyse neu starten"}</span>
        </button>
      </div>
    </header>
  );
}
