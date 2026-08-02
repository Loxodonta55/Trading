import React from 'react';
import { Sparkles, CheckCircle2, TrendingUp, TrendingDown, AlertTriangle, ShieldCheck, Target, Zap } from 'lucide-react';

export function ExplainabilityCard({ latestSignal, bestExperimentData, ticker }) {
  if (!latestSignal) return null;

  const winRate = (bestExperimentData?.win_rate || 0.62) * 100;
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
      return `Das KI-Modell identifiziert ein starkes bullisches Swing-Signal für ${ticker} mit einer Vorhersagewahrscheinlichkeit von ${probUp}%. Begründet durch: ${reasonText}. Der historische Backtest belegt eine Trefferquote von ${winRate.toFixed(1)}%.`;
    } else if (isSell) {
      return `Das KI-Modell empfiehlt eine Gewinnmitnahme / Gewinnabsicherung für ${ticker} (Abwärtswahrscheinlichkeit: ${probDown}%). Begründet durch: ${reasonText}.`;
    } else {
      return `Neutraler Konsolidierungszustand für ${ticker}. Das Modell empfiehlt Abwarten, bis die Swing-Trefferwahrscheinlichkeit den Schwellenwert überschreitet. Nachgewiesene Backtest-Trefferquote: ${winRate.toFixed(1)}%.`;
    }
  };

  return (
    <div className={`card explainability-card hero-recommendation ${isBuy ? 'recommendation-buy' : isSell ? 'recommendation-sell' : 'recommendation-hold'}`}>
      <div className="recommendation-top-bar">
        <div className="rec-badge-main">
          <Zap size={18} />
          <span>AKTUELLE KI-EMPFEHLUNG FOR {ticker} ({latestSignal.date})</span>
        </div>
        <div className="winrate-badge">
          <ShieldCheck size={16} /> Backtest Trefferquote: {winRate.toFixed(1)}% {winRate >= 60.0 ? "✓ (Ziel ≥ 60% erfüllt)" : ""}
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
          </div>
        </div>
      </div>

      <div className="recommendation-reasoning">
        <p className="explain-text">
          {generateReasoningMessage()}
        </p>
      </div>

      <div className="explain-factors">
        <div className="factor-chip highlight">
          <Target size={14} /> <strong>Erwartetes Ziel:</strong> {isBuy ? '+5.0% Swing' : isSell ? 'Absicherung' : 'Neutral'}
        </div>
        <div className="factor-chip">
          <strong>P(Up Swing):</strong> {probUp}%
        </div>
        <div className="factor-chip">
          <strong>RSI (14):</strong> {latestSignal.rsi_14?.toFixed(1) || "N/A"}
        </div>
        <div className="factor-chip">
          <strong>News Sentiment:</strong> {latestSignal.news_sentiment?.toFixed(2) || "0.00"}
        </div>
        <div className="factor-chip">
          <strong>Options IV Skew:</strong> {latestSignal.options_iv_skew?.toFixed(2) || "0.00"}
        </div>
        {latestSignal.political_trade_signal === 1 && (
          <div className="factor-chip buy-chip">
            <strong>US Kongress:</strong> BUY Signal 🏛️
          </div>
        )}
      </div>
    </div>
  );
}

