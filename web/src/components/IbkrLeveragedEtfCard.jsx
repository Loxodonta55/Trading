import React, { useState } from 'react';
import { Copy, Check, ExternalLink, ShieldCheck, Zap, TrendingUp, TrendingDown, Info } from 'lucide-react';
import { LEVERAGED_ETFS } from '../constants/leveragedEtfs';

export function IbkrLeveragedEtfCard({ ticker, latestSignal }) {
  const [copiedId, setCopiedId] = useState(null);

  const etfData = LEVERAGED_ETFS[ticker] || LEVERAGED_ETFS.TSLA;
  const isBuy = latestSignal?.signal === 1;
  const isSell = latestSignal?.signal === -1;

  const handleCopy = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => {
      setCopiedId(null);
    }, 2000);
  };

  return (
    <div className="card ibkr-etf-card">
      <div className="ibkr-etf-header">
        <div className="ibkr-title-area">
          <div className="ibkr-badge">
            <Zap size={15} />
            <span>INTERACTIVE BROKERS (IBKR) HEBEL-ETF IDENTIFIERS</span>
          </div>
          <h4 className="ibkr-subtitle">
            Hebel-Instrumente für Swing-Trades auf <strong>{etfData.name} ({ticker})</strong>
          </h4>
        </div>
        <div className="ibkr-hint-chip">
          <ShieldCheck size={14} color="#10B981" />
          <span>Direkt handelbar in IBKR TWS & IBKR Mobile</span>
        </div>
      </div>

      {/* Dynamic Recommendation Banner according to signal */}
      <div className={`ibkr-signal-action-box ${isBuy ? 'action-buy' : isSell ? 'action-sell' : 'action-neutral'}`}>
        <div className="action-icon">
          {isBuy ? <TrendingUp size={22} /> : isSell ? <TrendingDown size={22} /> : <Info size={22} />}
        </div>
        <div className="action-text">
          {isBuy ? (
            <div>
              <strong>🚀 Handelsempfehlung bei Kurssprung:</strong> Kaufe den <strong>{etfData.longUS.leverage} ETF ({etfData.longUS.ticker})</strong> oder für EU-Konten <strong>({etfData.longEU.ticker})</strong>, um den prognostizierten +5% Kurssprung gehebelt zu monetarisieren.
            </div>
          ) : isSell ? (
            <div>
              <strong>📉 Empfehlung zur Gewinnabsicherung:</strong> Position schließen oder Absicherung über <strong>{etfData.shortUS.ticker} ({etfData.shortUS.leverage})</strong> / <strong>{etfData.shortEU.ticker}</strong> prüfen.
            </div>
          ) : (
            <div>
              <strong>👁️ Konsolidierungsphase:</strong> Aktuell kein aktiver Kurssprung. Für zukünftige Long-Swings den Identifier <strong>{etfData.longUS.ticker}</strong> / <strong>{etfData.longEU.ticker}</strong> auf der IBKR Watchlist vormerken.
            </div>
          )}
        </div>
      </div>

      {/* Grid with US and EU/UCITS ETF Identifiers */}
      <div className="ibkr-etf-grid">
        {/* US Account Long ETF */}
        <div className="ibkr-etf-item highlight-bull">
          <div className="etf-type-tag bull">
            <TrendingUp size={13} /> BULL / LONG (US-KONTO)
          </div>
          <div className="etf-main-row">
            <div className="etf-ticker-large">{etfData.longUS.ticker}</div>
            <div className="etf-leverage-badge">{etfData.longUS.leverage}</div>
            <button
              className={`copy-btn ${copiedId === 'longUS' ? 'copied' : ''}`}
              onClick={() => handleCopy(etfData.longUS.ticker, 'longUS')}
              title="Ticker kopieren"
            >
              {copiedId === 'longUS' ? <><Check size={13} /> Kopiert</> : <><Copy size={13} /> Kopieren</>}
            </button>
          </div>
          <div className="etf-name">{etfData.longUS.name}</div>
          <div className="etf-details-row">
            <span>Börse: <strong>{etfData.longUS.exchange}</strong></span>
            <span>ISIN: <strong>{etfData.longUS.isin}</strong></span>
          </div>
        </div>

        {/* EU/UCITS Account Long ETF (for German/EU residents) */}
        <div className="ibkr-etf-item highlight-bull">
          <div className="etf-type-tag bull">
            <TrendingUp size={13} /> BULL / LONG (EU / UCITS KONTO)
          </div>
          <div className="etf-main-row">
            <div className="etf-ticker-large">{etfData.longEU.ticker}</div>
            <div className="etf-leverage-badge">{etfData.longEU.leverage}</div>
            <button
              className={`copy-btn ${copiedId === 'longEU' ? 'copied' : ''}`}
              onClick={() => handleCopy(etfData.longEU.ticker, 'longEU')}
              title="Ticker kopieren"
            >
              {copiedId === 'longEU' ? <><Check size={13} /> Kopiert</> : <><Copy size={13} /> Kopieren</>}
            </button>
          </div>
          <div className="etf-name">{etfData.longEU.name}</div>
          <div className="etf-details-row">
            <span>Börse: <strong>{etfData.longEU.exchange}</strong></span>
            <span>ISIN: <strong>{etfData.longEU.isin}</strong></span>
          </div>
        </div>

        {/* US Account Short ETF */}
        <div className="ibkr-etf-item">
          <div className="etf-type-tag bear">
            <TrendingDown size={13} /> BEAR / SHORT (US-KONTO)
          </div>
          <div className="etf-main-row">
            <div className="etf-ticker-large">{etfData.shortUS.ticker}</div>
            <div className="etf-leverage-badge">{etfData.shortUS.leverage}</div>
            <button
              className={`copy-btn ${copiedId === 'shortUS' ? 'copied' : ''}`}
              onClick={() => handleCopy(etfData.shortUS.ticker, 'shortUS')}
              title="Ticker kopieren"
            >
              {copiedId === 'shortUS' ? <><Check size={13} /> Kopiert</> : <><Copy size={13} /> Kopieren</>}
            </button>
          </div>
          <div className="etf-name">{etfData.shortUS.name}</div>
          <div className="etf-details-row">
            <span>Börse: <strong>{etfData.shortUS.exchange}</strong></span>
            <span>ISIN: <strong>{etfData.shortUS.isin}</strong></span>
          </div>
        </div>

        {/* EU/UCITS Account Short ETF */}
        <div className="ibkr-etf-item">
          <div className="etf-type-tag bear">
            <TrendingDown size={13} /> BEAR / SHORT (EU / UCITS)
          </div>
          <div className="etf-main-row">
            <div className="etf-ticker-large">{etfData.shortEU.ticker}</div>
            <div className="etf-leverage-badge">{etfData.shortEU.leverage}</div>
            <button
              className={`copy-btn ${copiedId === 'shortEU' ? 'copied' : ''}`}
              onClick={() => handleCopy(etfData.shortEU.ticker, 'shortEU')}
              title="Ticker kopieren"
            >
              {copiedId === 'shortEU' ? <><Check size={13} /> Kopiert</> : <><Copy size={13} /> Kopieren</>}
            </button>
          </div>
          <div className="etf-name">{etfData.shortEU.name}</div>
          <div className="etf-details-row">
            <span>Börse: <strong>{etfData.shortEU.exchange}</strong></span>
            <span>ISIN: <strong>{etfData.shortEU.isin}</strong></span>
          </div>
        </div>
      </div>

      {/* Optional Special Track (e.g. SpaceX DXYZ) */}
      {etfData.specialTrack && (
        <div className="ibkr-special-track">
          <span className="special-badge">SPACEX TRACKING AUF IBKR</span>
          <span className="special-text">
            Für direkte SpaceX Pre-IPO Beteiligung auf Interactive Brokers: Ticker <strong>{etfData.specialTrack.ticker}</strong> ({etfData.specialTrack.name}, ISIN: {etfData.specialTrack.isin})
          </span>
          <button
            className={`copy-btn ${copiedId === 'specialTrack' ? 'copied' : ''}`}
            onClick={() => handleCopy(etfData.specialTrack.ticker, 'specialTrack')}
            title="Ticker kopieren"
          >
            {copiedId === 'specialTrack' ? <><Check size={13} /> Kopiert</> : <><Copy size={13} /> Kopieren</>}
          </button>
        </div>
      )}
    </div>
  );
}
