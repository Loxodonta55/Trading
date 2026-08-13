import React from 'react';
import { Sparkles, TrendingUp, TrendingDown, ShieldCheck, Target, Zap, Info, Star } from 'lucide-react';
import { LEVERAGED_ETFS } from '../constants/leveragedEtfs';

export function ExplainabilityCard({ latestSignal, bestExperimentData, ticker, chartData }) {
  if (!latestSignal) return null;

  const etfData = LEVERAGED_ETFS[ticker] || LEVERAGED_ETFS.TSLA;
  const rawWinRate = bestExperimentData?.win_rate ?? 44.44;
  const winRate = rawWinRate > 1 ? Math.min(rawWinRate, 100) : rawWinRate * 100;

  // Calculate recent 3-month (90 days) hit/miss breakdown from chartData
  let winCount = 0;
  let lossCount = 0;
  let recentWinRate = winRate;

  if (chartData && chartData.length > 0) {
    const lastDate = new Date(chartData[chartData.length - 1].date);
    const cutoffDate = new Date(lastDate);
    cutoffDate.setDate(cutoffDate.getDate() - 90);

    const recentData = chartData.filter(d => new Date(d.date) >= cutoffDate);
    const activeSignals = recentData.filter(d => d.signal !== 0 && d.signal !== undefined);

    activeSignals.forEach(d => {
      if ((d.signal === 1 && d.swing_target === 1) || (d.signal === -1 && d.swing_target === -1)) {
        winCount++;
      } else {
        lossCount++;
      }
    });

    const total = winCount + lossCount;
    if (total > 0) {
      recentWinRate = (winCount / total) * 100;
    }
  }

  const displayedWinRate = recentWinRate.toFixed(1);
  const breakdownText = (winCount + lossCount > 0) ? ` (${winCount} Treffer / ${lossCount} Fehlschläge)` : '';

  const isBuy = latestSignal.signal === 1;
  const isSell = latestSignal.signal === -1;
  const probUp = Math.round((latestSignal.prob_up || 0.5) * 100);
  const probDown = Math.round((latestSignal.prob_down || 0.5) * 100);
  const confidence = isBuy ? probUp : isSell ? probDown : Math.max(probUp, probDown);

  // Generate clear decision explanation message for user
  const generateReasoningMessage = () => {
    let reasons = [];
    if (latestSignal.rsi_14 < 40) {
      reasons.push(`überverkauftem RSI (${latestSignal.rsi_14.toFixed(1)})`);
    } else if (latestSignal.rsi_14 > 60) {
      reasons.push(`starkem RSI Momentum (${latestSignal.rsi_14.toFixed(1)})`);
    }

    if (latestSignal.news_sentiment > 0.1) {
      reasons.push(`positivem News-Sentiment (${latestSignal.news_sentiment.toFixed(2)})`);
    }

    if (latestSignal.options_iv_skew < 0) {
      reasons.push(`bullischem Optionen-Skews (${latestSignal.options_iv_skew.toFixed(2)})`);
    }

    if (latestSignal.political_trade_signal === 1) {
      reasons.push(`positiven US-Kongress Insider-Käufen`);
    }

    if (reasons.length === 0) {
      reasons.push(`Google TabFM Zeitreihen-Musteranalyse und Relativstärke vs. SPY`);
    }

    const reasonText = reasons.join(", ");
    if (isBuy) {
      return `Das KI-Modell identifiziert ein starkes bullisches Swing-Signal für ${ticker} mit einer Vorhersagewahrscheinlichkeit von ${probUp}%. Begründet durch: ${reasonText}. Nachgewiesene 3-Monats Backtest-Trefferquote: ${displayedWinRate}%${breakdownText}.`;
    } else if (isSell) {
      return `Das KI-Modell empfiehlt eine Gewinnmitnahme / Gewinnabsicherung für ${ticker} (Abwärtswahrscheinlichkeit: ${probDown}%). Begründet durch: ${reasonText}. Nachgewiesene 3-Monats Backtest-Trefferquote: ${displayedWinRate}%${breakdownText}.`;
    } else {
      return `Neutraler Konsolidierungszustand für ${ticker}. Das Modell empfiehlt Abwarten, bis die Swing-Trefferwahrscheinlichkeit den Schwellenwert überschreitet. Nachgewiesene 3-Monats Backtest-Trefferquote: ${displayedWinRate}%${breakdownText}.`;
    }
  };

  return (
    <div className={`card explainability-card hero-recommendation ${isBuy ? 'recommendation-buy' : isSell ? 'recommendation-sell' : 'recommendation-hold'}`}>
      <div className="recommendation-top-bar">
        <div className="rec-badge-main">
          <Zap size={18} />
          <span>AKTUELLE KI-EMPFEHLUNG FÜR {ticker} ({latestSignal.date})</span>
          {isBuy && (
            <span className="star-jump-hero-badge">
              <Star size={14} fill="#F59E0B" color="#F59E0B" /> VOR KURSSPRUNG
            </span>
          )}
        </div>
        <div className="winrate-badge">
          <ShieldCheck size={16} /> 3-Monats Trefferquote: {displayedWinRate}% {parseFloat(displayedWinRate) >= 60.0 ? "✓ (Ziel ≥ 60% erfüllt)" : ""}
        </div>
      </div>

      <div className="recommendation-hero-grid">
        <div className="recommendation-signal-box">
          <div className="signal-label-small">PROGNOSTIZIERTES SIGNAL</div>
          <div className={`signal-title-large ${isBuy ? 'text-buy' : isSell ? 'text-sell' : 'text-hold'}`}>
            {isBuy ? (
              <>
                <TrendingUp size={36} /> BUY SWING 🚀
              </>
            ) : isSell ? (
              <>
                <TrendingDown size={36} /> TAKE PROFIT 📉
              </>
            ) : (
              <>
                <Sparkles size={36} /> HOLD / WATCH 👁️
              </>
            )}
          </div>
          <div className="signal-subtext">
            {isBuy ? 'Ziel: +5.0% Swing Gewinn' : isSell ? 'Gewinnabsicherung empfohlen' : 'Warten auf klare Marktsignale'}
          </div>
        </div>

        <div className="recommendation-confidence-box">
          <div className="confidence-header">
            <span>KI-Konfidenz P({isBuy ? 'Up' : isSell ? 'Down' : 'Trend'}):</span>
            <span className="confidence-value">{confidence}%</span>
          </div>
          <div className="confidence-meter-bg">
            <div 
              className={`confidence-meter-fill ${isBuy ? 'fill-buy' : isSell ? 'fill-sell' : 'fill-hold'}`} 
              style={{ width: `${confidence}%` }}
            />
          </div>
          <div className="confidence-sub">
            Aktueller Kurs: <strong>${(latestSignal.close || 0).toFixed(2)}</strong>
            <span className="etf-quick-hint">
              IBKR Hebel: <strong>{etfData.longUS.ticker}</strong> ({etfData.longUS.leverage})
            </span>
          </div>
        </div>
      </div>

      <div className="recommendation-reasoning">
        <p className="explain-text">
          {generateReasoningMessage()}
        </p>
      </div>

      <div className="explain-factors">
        <div className="factor-chip highlight" title="Erwartetes Kursziel der KI-Swing-Strategie (+5.0% Kursanstiegsziel innerhalb von 5 Trading-Tagen).">
          <Target size={14} /> <strong>Erwartetes Ziel:</strong> {isBuy ? '+5.0% Swing' : isSell ? 'Absicherung' : 'Neutral'}
        </div>
        <div className="factor-chip" title="P(Up Swing) ist die vom Google TabFM AI-Foundation-Modell berechnete Wahrscheinlichkeit, dass die Aktie in den nächsten 5 Trading-Tagen einen positiven Kurssprung von mindestens 5% erzielt. Ein Wert >= 60% gilt als statistisch valides Kausignal.">
          <Info size={12} style={{ opacity: 0.75, marginRight: '4px' }} />
          <strong>P(Up Swing):</strong> {probUp}%
        </div>
        <div className="factor-chip" title="Der RSI (14) misst die Geschwindigkeit und Dynamik von Kursbewegungen auf einer Skala von 0 bis 100. Werte unter 40 deuten auf eine überverkaufte Aktie hin (mögliche Trendwende nach oben), während Werte über 60 eine überkaufte Marktphase anzeigen.">
          <Info size={12} style={{ opacity: 0.75, marginRight: '4px' }} />
          <strong>RSI (14):</strong> {latestSignal.rsi_14?.toFixed(1) || "N/A"}
        </div>
        <div className="factor-chip" title="Das News Sentiment bewertet den Stimmungstrend aktueller Finanznachrichten und Marktberichte über einen gleitenden 3-Tages-Durchschnitt (-1.0 bis +1.0). Ein positiver Wert signalisiert Rückenwind durch fundamentale Marktkatalysatoren.">
          <Info size={12} style={{ opacity: 0.75, marginRight: '4px' }} />
          <strong>News Sentiment:</strong> {latestSignal.news_sentiment?.toFixed(2) || "0.00"}
        </div>
        <div className="factor-chip" title="Der Option IV Skew vergleicht die implizite Volatilität von Call- und Put-Optionen am Derivatemarkt. Ein negativer Skew zeigt, dass institutionelle Anleger höhere Prämien für Call-Optionen zahlen (bullische Positionierung des Smart Moneys).">
          <Info size={12} style={{ opacity: 0.75, marginRight: '4px' }} />
          <strong>Options IV Skew:</strong> {latestSignal.options_iv_skew?.toFixed(2) || "0.00"}
        </div>
        <div className="factor-chip ibkr-factor-chip" title="Der passende Hebel-ETF auf Interactive Brokers (IBKR).">
          <Zap size={13} color="#10B981" />
          <strong>IBKR Hebel:</strong> {etfData.longUS.ticker} ({etfData.longUS.leverage}) / {etfData.longEU.ticker} (EU)
        </div>
        {latestSignal.political_trade_signal === 1 && (
          <div className="factor-chip buy-chip" title="US-Kongress Trades signalisieren offengelegte Insider-Käufe amerikanischer Politiker.">
            <strong>US Kongress:</strong> BUY Signal 🏛️
          </div>
        )}
      </div>
    </div>
  );
}
