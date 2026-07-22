import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from config import SWING_HORIZON_DAYS, SWING_UP_THRESHOLD, SWING_DOWN_THRESHOLD
from src.data.fetcher import MarketDataFetcher
from src.data.news_fetcher import NewsFetcher
from src.data.political_fetcher import PoliticalTradesFetcher
from src.data.social_fetcher import SocialFetcher
from src.data.sec_fetcher import SecFetcher

class FeatureBuilder:
    """
    Compiles multi-source features (Technicals, Macro, News, SEC Filings, Political Trades, Social Sentiment)
    and constructs forward-looking swing labels for TabFM training & walk-forward backtesting.
    """
    def __init__(self):
        self.market_fetcher = MarketDataFetcher()
        self.news_fetcher = NewsFetcher()
        self.pol_fetcher = PoliticalTradesFetcher()
        self.soc_fetcher = SocialFetcher()
        self.sec_fetcher = SecFetcher()

    def build_dataset(self) -> pd.DataFrame:
        print("[FeatureBuilder] Building dataset from multi-source data feeds...")
        # 1. Primary Stock Data (TSLA)
        df = self.market_fetcher.fetch_primary_data()
        
        # 2. Market Macro Benchmarks (SPY, QQQ, VIX)
        macro_df = self.market_fetcher.fetch_benchmark_data()
        if not macro_df.empty:
            df = df.join(macro_df, how='left').ffill()

        # 3. Technical Features
        df = self._add_technical_features(df)

        # 4. News Sentiment Features
        news_df = self.news_fetcher.fetch_news_features(df.index)
        df = df.join(news_df, how='left')

        # 5. Event-Driven News Catalyst & Lead-Lag Transformations
        df = self._add_event_catalyst_features(df)

        # 6. Official SEC EDGAR Filings & Disclosure Features
        sec_df = self.sec_fetcher.fetch_sec_features(df.index)
        df = df.join(sec_df, how='left')

        # 7. Political Trade Features
        pol_df = self.pol_fetcher.fetch_political_features(df.index)
        df = df.join(pol_df, how='left')

        # 8. Social Media Features
        soc_df = self.soc_fetcher.fetch_social_features(df.index)
        df = df.join(soc_df, how='left')

        # 8. Construct Forward Target Labels (strictly for training labels, not features!)
        df = self._add_swing_targets(df)

        # Drop warm-up rows with NaN values in core indicators
        df = df.dropna(subset=['rsi_14', 'macd', 'atr_14'])
        
        print(f"[FeatureBuilder] Final Feature Dataset Shape: {df.shape}")
        return df

    def _add_technical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        # Multi-period returns
        df['return_1d'] = df['close'].pct_change(1)
        df['return_3d'] = df['close'].pct_change(3)
        df['return_5d'] = df['close'].pct_change(5)
        df['return_10d'] = df['close'].pct_change(10)

        # Moving Averages & Ratios
        ema9 = df['close'].ewm(span=9, adjust=False).mean()
        ema21 = df['close'].ewm(span=21, adjust=False).mean()
        ema50 = df['close'].ewm(span=50, adjust=False).mean()
        
        df['ema_9_ratio'] = (df['close'] / ema9) - 1.0
        df['ema_21_ratio'] = (df['close'] / ema21) - 1.0
        df['ema_50_ratio'] = (df['close'] / ema50) - 1.0

        # RSI 14
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / (loss + 1e-9)
        df['rsi_14'] = 100 - (100 / (1 + rs))

        # MACD
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema12 - ema26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']

        # ATR 14
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift(1)).abs()
        low_close = (df['low'] - df['close'].shift(1)).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr_14'] = tr.rolling(14).mean()
        df['atr_ratio'] = df['atr_14'] / df['close']

        # Bollinger Bands (20, 2)
        sma20 = df['close'].rolling(20).mean()
        std20 = df['close'].rolling(20).std()
        upper_bb = sma20 + (std20 * 2)
        lower_bb = sma20 - (std20 * 2)
        df['bollinger_pos'] = (df['close'] - lower_bb) / (upper_bb - lower_bb + 1e-9)
        df['bollinger_width'] = (upper_bb - lower_bb) / (sma20 + 1e-9)

        # Volume ratio
        df['volume_ratio_5d'] = df['volume'] / (df['volume'].rolling(5).mean() + 1e-9)

        # Macro relative metrics
        if 'spy_close' in df.columns:
            df['spy_return_1d'] = df['spy_close'].pct_change(1)
            df['tsla_vs_spy_rel_strength'] = df['return_1d'] - df['spy_return_1d']

        if 'vix_close' in df.columns:
            df['vix_change_1d'] = df['vix_close'].pct_change(1)

        return df

    def _add_event_catalyst_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transforms raw news sentiment into event-driven catalyst flags and lead-lag signals.
        Filters out raw noise by isolating significant sentiment surges & news catalyst events.
        """
        if 'news_sentiment' in df.columns:
            # 1. Sentiment anomaly / spike (|sentiment - 3d_ma| > 0.25)
            diff_from_ma = (df['news_sentiment'] - df['news_sentiment_3d_ma']).abs()
            df['news_sentiment_spike'] = (diff_from_ma > 0.25).astype(int)

            # 2. News Catalyst Gate: Active when press release OR major news spike occurs
            df['news_catalyst_gate'] = ((df['press_release_flag'] == 1) | (df['news_sentiment_spike'] == 1)).astype(int)

            # 3. Lead-Lag Sentiment Signals (1-day & 2-day prior sentiment lead)
            df['news_lead_1d'] = df['news_sentiment'].shift(1).fillna(0.0)
            df['news_lead_2d'] = df['news_sentiment'].shift(2).fillna(0.0)

            # 4. Tech + News Conviction Interaction (RSI divergence * catalyst gate)
            rsi_norm = (df['rsi_14'] - 50.0) / 50.0
            df['tech_news_conviction'] = rsi_norm * df['news_catalyst_gate']
        return df

    def _add_swing_targets(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Constructs target labels for predicting upcoming swings within SWING_HORIZON_DAYS.
        Label mapping:
          2 -> Swing Up (Forward max price movement >= +5%)
          0 -> Swing Down (Forward min price movement <= -5%)
          1 -> Neutral (No strong swing)
        """
        # Forward maximum return over next N days
        forward_max = df['high'].shift(-SWING_HORIZON_DAYS).rolling(SWING_HORIZON_DAYS).max()
        forward_max_return = (forward_max / df['close']) - 1.0

        # Forward minimum return over next N days
        forward_min = df['low'].shift(-SWING_HORIZON_DAYS).rolling(SWING_HORIZON_DAYS).min()
        forward_min_return = (forward_min / df['close']) - 1.0

        df['forward_max_return'] = forward_max_return
        df['forward_min_return'] = forward_min_return

        # Assign Swing Target Class
        targets = np.full(len(df), 1) # default 1 = Neutral
        
        up_mask = forward_max_return >= SWING_UP_THRESHOLD
        down_mask = forward_min_return <= SWING_DOWN_THRESHOLD
        
        # When both thresholds met, prioritize stronger move magnitude
        both_mask = up_mask & down_mask
        targets[up_mask] = 2
        targets[down_mask] = 0
        targets[both_mask] = np.where(forward_max_return[both_mask] > abs(forward_min_return[both_mask]), 2, 0)

        df['swing_target'] = targets
        return df

if __name__ == "__main__":
    builder = FeatureBuilder()
    full_df = builder.build_dataset()
    print("Class Distribution of Targets:")
    print(full_df['swing_target'].value_counts())
    print("\nSample Columns:")
    print(full_df[['close', 'return_1d', 'rsi_14', 'news_sentiment', 'political_trade_signal', 'x_sentiment_score', 'swing_target']].head())
