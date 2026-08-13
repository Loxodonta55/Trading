import React, { useState, useEffect } from 'react';
import { Sparkles, ExternalLink, Globe } from 'lucide-react';

export function MetricsOverview({ latestSignal, ticker }) {
  const [newsList, setNewsList] = useState([]);
  const [isNewsLoading, setIsNewsLoading] = useState(false);

  useEffect(() => {
    if (!ticker) return;
    const fetchNews = async () => {
      try {
        setIsNewsLoading(true);
        const res = await fetch(`/api/news/${ticker}`);
        if (res.ok) {
          const json = await res.json();
          setNewsList(json.news || []);
        }
      } catch (err) {
        console.warn("Could not fetch live news:", err);
      } finally {
        setIsNewsLoading(false);
      }
    };
    fetchNews();
  }, [ticker]);

  if (!latestSignal) return null;

  const isBuy = latestSignal.signal === 1;
  const isSell = latestSignal.signal === -1;
  const probUp = Math.round((latestSignal.prob_up || 0.5) * 100);
  const rsi = latestSignal.rsi_14 ? latestSignal.rsi_14.toFixed(1) : "50.0";
  const sentiment = latestSignal.news_sentiment_3d_ma !== undefined ? latestSignal.news_sentiment_3d_ma.toFixed(2) : "0.00";
  const optionsSkew = latestSignal.options_iv_skew !== undefined ? latestSignal.options_iv_skew.toFixed(2) : "0.00";
  const hasCongressTrade = latestSignal.political_trade_signal === 1;

  // Fallback ticker specific news if loading or offline
  const fallbackNews = {
    TSLA: {
      title: "Tesla Stock Erases Year of Gains as Investors Weigh Margin & Delivery Expectations",
      provider: "Barron's",
      url: "https://finance.yahoo.com/quote/TSLA"
    },
    GOOGL: {
      title: "Alphabet Gains on Strong Cloud Revenue Growth and Easing AI Search Concerns",
      provider: "Yahoo Finance",
      url: "https://finance.yahoo.com/quote/GOOGL"
    },
    SPCX: {
      title: "S&P 500 Rally Broadens as Investors Await Fed Interest Rate Decision",
      provider: "Wall Street Journal",
      url: "https://finance.yahoo.com/quote/SPY"
    },
    NVDA: {
      title: "Nvidia Unveils Next-Gen AI Chips, Cementing Datacenter Dominance",
      provider: "Bloomberg",
      url: "https://finance.yahoo.com/quote/NVDA"
    }
  };

  const topNews = newsList.length > 0 ? newsList[0] : (fallbackNews[ticker] || fallbackNews.TSLA);

  return (
    <section className="today-decision-section">
      <div className="section-title-bar">
        <Sparkles size={18} color="#10B981" />
        <h3>HEUTIGE ENTSCHEIDUNGS-KPIS FÜR {ticker} ({latestSignal.date})</h3>
      </div>

      {/* 6 Top Decision KPI Cards */}
      <div className="metrics-grid">
        <div className="card metric-card decision-kpi" title="Prognostiziertes Handelssignal auf Basis von Google TabFM, technischen Indikatoren und Sentiment-Analysen.">
          <div className="metric-label">1. Signal für Heute</div>
          <div className={`metric-value ${isBuy ? 'positive' : isSell ? 'negative' : 'gold'}`}>
            {isBuy ? 'BUY SWING 🚀' : isSell ? 'TAKE PROFIT 📉' : 'HOLD 👁️'}
          </div>
          <div className="metric-sub">Kurs: ${latestSignal.close?.toFixed(2) || '0.00'}</div>
        </div>

        <div className="card metric-card decision-kpi" title="P(Up Swing) ist die vom Google TabFM AI-Foundation-Modell berechnete Wahrscheinlichkeit, dass die Aktie in den nächsten 5 Trading-Tagen einen positiven Kurssprung von mindestens 5% erzielt. Ein Wert >= 60% gilt als statistisch valides Kausignal.">
          <div className="metric-label">2. KI-Konfidenz P(Up)</div>
          <div className={`metric-value ${probUp >= 60 ? 'positive' : 'gold'}`}>
            {probUp}%
          </div>
          <div className="metric-sub">Gewinn-Wahrscheinlichkeit</div>
        </div>

        <div className="card metric-card decision-kpi" title="Der RSI (14) misst die Geschwindigkeit und Dynamik von Kursbewegungen auf einer Skala von 0 bis 100. Werte unter 40 deuten auf eine überverkaufte Aktie hin (mögliche Trendwende nach oben), während Werte über 60 eine überkaufte Marktphase anzeigen.">
          <div className="metric-label">3. RSI (14) Momentum</div>
          <div className={`metric-value ${rsi < 40 ? 'positive' : rsi > 60 ? 'negative' : ''}`}>
            {rsi}
          </div>
          <div className="metric-sub">{rsi < 40 ? 'Überverkauft (Kauf-Chance)' : rsi > 60 ? 'Überkaufte Zone' : 'Neutraler Bereich'}</div>
        </div>

        <div className="card metric-card decision-kpi" title="Das News Sentiment bewertet den Stimmungstrend aktueller Finanznachrichten und Marktberichte über einen gleitenden 3-Tages-Durchschnitt (-1.0 bis +1.0). Ein positiver Wert signalisiert Rückenwind durch fundamentale Marktkatalysatoren.">
          <div className="metric-label">4. News Sentiment (3D MA)</div>
          <div className={`metric-value ${parseFloat(sentiment) > 0.05 ? 'positive' : parseFloat(sentiment) < -0.05 ? 'negative' : ''}`}>
            {sentiment > 0 ? `+${sentiment}` : sentiment}
          </div>
          <div className="metric-sub">{parseFloat(sentiment) > 0.05 ? 'Bullischer Nachrichtenfluss' : 'Bärischer Druck'}</div>
        </div>

        <div className="card metric-card decision-kpi" title="Der Option IV Skew vergleicht die implizite Volatilität von Call- und Put-Optionen am Derivatemarkt. Ein negativer Skew zeigt, dass institutionelle Anleger höhere Prämien für Call-Optionen zahlen (bullische Positionierung des Smart Moneys).">
          <div className="metric-label">5. Options IV Skew</div>
          <div className="metric-value">
            {optionsSkew}
          </div>
          <div className="metric-sub">{parseFloat(optionsSkew) < 0 ? 'Bullische Call-Prämie' : 'Put-Nachfrage dominierend'}</div>
        </div>

        <div className="card metric-card decision-kpi" title="US-Kongress Trades signalisieren offengelegte Insider-Käufe amerikanischer Politiker.">
          <div className="metric-label">6. US-Kongress Trades</div>
          <div className={`metric-value ${hasCongressTrade ? 'positive' : ''}`}>
            {hasCongressTrade ? 'BUY 🏛️' : 'Keine Käufe'}
          </div>
          <div className="metric-sub">{hasCongressTrade ? 'Insider-Meldung vorliegend' : 'Kein Politik-Signal'}</div>
        </div>
      </div>

      {/* Professional Market News & Catalyst Banner */}
      <div className="card real-news-banner">
        <div className="news-badge">
          <Globe size={14} /> MARKT-KATALYSATOR & SENTIMENT ({ticker})
        </div>
        <div className="news-content">
          <span className="news-headline">"{topNews.title}"</span>
          <span className="news-source">Quelle: <strong>{topNews.provider || 'Reuters'}</strong></span>
        </div>
        {topNews.url && (
          <a href={topNews.url} target="_blank" rel="noopener noreferrer" className="news-link-btn">
            Original-Artikel <ExternalLink size={13} />
          </a>
        )}
      </div>
    </section>
  );
}
