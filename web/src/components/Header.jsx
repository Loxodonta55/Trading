import React from 'react';
import { RefreshCw, Activity, ShieldCheck } from 'lucide-react';

export function Header({ onRunPipeline, isLoading }) {
  return (
    <header class="app-header">
      <div class="logo-area">
        <div class="logo-badge">TabFM</div>
        <div>
          <h1>Trading Swing Predictor (React SPA)</h1>
          <p class="subtitle">Spec-Driven Development Architecture | Multi-Source Google TabFM Engine</p>
        </div>
      </div>
      <div class="header-actions">
        <span class="status-chip live">
          <span class="pulse"></span> TabFM 2026 Engine Active
        </span>
        <span class="status-chip">
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
