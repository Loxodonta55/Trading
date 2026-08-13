import React from 'react';
import { Star, Sparkles, TrendingUp, ArrowRight, ShieldCheck } from 'lucide-react';
import { LEVERAGED_ETFS } from '../constants/leveragedEtfs';

export function JumpRadarBanner({ tickersStatus, activeTicker, onSelectTicker }) {
  if (!tickersStatus) return null;

  const jumpTickers = Object.entries(tickersStatus).filter(([_, info]) => info.isJumpPending);
  const latestDate = Object.values(tickersStatus)[0]?.date || 'Heute';

  const hasJumpingStock = jumpTickers.length > 0;

  return (
    <div className={`card jump-radar-banner ${hasJumpingStock ? 'has-jump-alert' : 'radar-neutral'}`}>
      <div className="radar-header">
        <div className="radar-title-group">
          <div className={`star-icon-container ${hasJumpingStock ? 'star-pulsing' : ''}`}>
            <Star size={20} className="star-icon" fill={hasJumpingStock ? "#F59E0B" : "none"} color="#F59E0B" />
          </div>
          <div>
            <h3 className="radar-title">
              {hasJumpingStock ? (
                <>⭐ KI-KURSSPRUNG ALARM — AKTIE VOR SPRUNG ENTDECKT! ({latestDate})</>
              ) : (
                <>⭐ KI-KURSSPRUNG RADAR (Stand: {latestDate})</>
              )}
            </h3>
            <p className="radar-subtitle">
              {hasJumpingStock
                ? `Das Google TabFM KI-Modell signalisiert heute für ${jumpTickers.length} von 4 Aktien einen bevorstehenden Kurssprung (+5% Swing Up).`
                : `Automatische Überwachung aller 4 Fokus-Aktien auf bevorstehende Kurssprünge (+5% Swing Up). Sobald ein Wert ein Kaufsignal generiert, wird er mit einem goldenen Stern ⭐ markiert.`}
            </p>
          </div>
        </div>
        <div className="radar-status-badge">
          {hasJumpingStock ? (
            <span className="badge-alert">
              <Sparkles size={14} /> {jumpTickers.length} Sprung-Signal{jumpTickers.length > 1 ? 'e' : ''} aktiv
            </span>
          ) : (
            <span className="badge-watching">
              <ShieldCheck size={14} /> 4 Werte unter Beobachtung
            </span>
          )}
        </div>
      </div>

      {/* If any stock is poised for a jump, show rich action cards */}
      {hasJumpingStock ? (
        <div className="jump-stocks-container">
          {jumpTickers.map(([sym, info]) => {
            const etf = LEVERAGED_ETFS[sym] || {};
            const isSelected = activeTicker === sym;
            return (
              <div 
                key={sym} 
                className={`jump-stock-chip ${isSelected ? 'selected' : ''}`}
                onClick={() => onSelectTicker(sym)}
              >
                <div className="chip-star">
                  <Star size={16} fill="#F59E0B" color="#F59E0B" />
                </div>
                <div className="chip-info">
                  <span className="chip-name">{info.name} ({sym})</span>
                  <span className="chip-prob">P(Up Swing): <strong>{Math.round((info.prob_up || 0.6) * 100)}%</strong></span>
                </div>
                <div className="chip-etf-tag">
                  <span>IBKR Hebel: <strong>{etf.longUS?.ticker || 'TSLL'} ({etf.longUS?.leverage || '2x'})</strong></span>
                </div>
                <button className="chip-action-btn">
                  <span>Details</span>
                  <ArrowRight size={13} />
                </button>
              </div>
            );
          })}
        </div>
      ) : (
        /* Quick Radar overview across all 4 stocks */
        <div className="radar-stocks-row">
          {Object.entries(tickersStatus).map(([sym, info]) => {
            const etf = LEVERAGED_ETFS[sym] || {};
            const probUp = Math.round((info.prob_up || 0) * 100);
            const isSelected = activeTicker === sym;
            return (
              <div
                key={sym}
                className={`radar-ticker-pill ${isSelected ? 'pill-active' : ''}`}
                onClick={() => onSelectTicker(sym)}
                title={`Klicken für Analyse von ${info.name}`}
              >
                <div className="pill-top">
                  <span className="pill-sym">{sym}</span>
                  <span className="pill-prob">{probUp}% P(Up)</span>
                </div>
                <div className="pill-bottom">
                  <span>IBKR: <strong>{etf.longUS?.ticker}</strong></span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
