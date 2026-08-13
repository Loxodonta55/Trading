import logging
import pandas as pd
import numpy as np
from pathlib import Path

from config import SWING_HORIZON_DAYS, SWING_UP_THRESHOLD, SWING_DOWN_THRESHOLD
from src.data.fetcher import MarketDataFetcher
from src.data.news_fetcher import NewsFetcher
from src.data.political_fetcher import PoliticalTradesFetcher
from src.data.social_fetcher import SocialFetcher
from src.data.sec_fetcher import SecFetcher
from src.data.options_fetcher import OptionsFetcher
from src.data.sec_text_processor import SecTextProcessor

logger = logging.getLogger(__name__)

class FeatureBuilder:
    """
    Compiles multi-source features (Technicals, Macro, News, SEC Filings, SEC Unstructured Text, Options Chain, Social Sentiment)
    and constructs forward-looking swing labels for TabFM training & walk-forward backtesting.
    """
    RSI_PERIOD = 14
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    ATR_PERIOD = 14
    BB_PERIOD = 20
    BB_STD = 2

    def __init__(self, ticker: str = "TSLA") -> None:
        """
        Initializes the FeatureBuilder.

        Args:
            ticker: The primary stock ticker.
        """
        self.ticker = ticker
        self.market_fetcher = MarketDataFetcher(ticker=ticker)
        self.news_fetcher = NewsFetcher(ticker=ticker)
        self.pol_fetcher = PoliticalTradesFetcher(ticker=ticker)
        self.soc_fetcher = SocialFetcher(ticker=ticker)
        self.sec_fetcher = SecFetcher(ticker=ticker)
        self.sec_text_processor = SecTextProcessor(ticker=ticker)
        self.opt_fetcher = OptionsFetcher(ticker=ticker)

    def build_dataset(self) -> pd.DataFrame:
        """
        Builds the complete dataset for the ticker.

        Returns:
            A pandas DataFrame containing all features and targets.
        """
        logger.info(f"[FeatureBuilder] Building dataset for {self.ticker} from multi-source data feeds...")
        # 1. Primary Stock Data (TSLA / GOOGL)
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

        # 6. Official SEC EDGAR Filings & Structured Features
        sec_df = self.sec_fetcher.fetch_sec_features(df.index)
        df = df.join(sec_df, how='left')

        # 7. Unstructured SEC Document NLP Text Features (Risk Drift & MD&A Sentiment)
        sec_text_df = self.sec_text_processor.fetch_sec_text_features(df.index)
        df = df.join(sec_text_df, how='left')

        # 8. Institutional Options Market & Put/Call Sentiment Features
        opt_df = self.opt_fetcher.fetch_options_features(df.index)
        df = df.join(opt_df, how='left')

        # 9. Political Trade Features
        pol_df = self.pol_fetcher.fetch_political_features(df.index)
        df = df.join(pol_df, how='left')

        # 10. Social Media Features
        soc_df = self.soc_fetcher.fetch_social_features(df.index)
        df = df.join(soc_df, how='left')

        # Construct Forward Target Labels (strictly for training labels, not features!)
        df = self._add_swing_targets(df)

        # Drop warm-up rows with NaN values in core indicators
        df = df.dropna(subset=['rsi_14', 'macd', 'atr_14'])
        
        logger.info(f"[FeatureBuilder] Final Feature Dataset Shape: {df.shape}")
        return df

    def _add_technical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates and adds technical features to the dataframe.

        Args:
            df: The dataframe containing price data.

        Returns:
            The dataframe with technical features added.
        """
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
        gain = (delta.where(delta > 0, 0)).rolling(self.RSI_PERIOD).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.RSI_PERIOD).mean()
        rs = gain / (loss + 1e-9)
        df['rsi_14'] = 100 - (100 / (1 + rs))

        # MACD
        ema12 = df['close'].ewm(span=self.MACD_FAST, adjust=False).mean()
        ema26 = df['close'].ewm(span=self.MACD_SLOW, adjust=False).mean()
        df['macd'] = ema12 - ema26
        df['macd_signal'] = df['macd'].ewm(span=self.MACD_SIGNAL, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']

        # ATR 14
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift(1)).abs()
        low_close = (df['low'] - df['close'].shift(1)).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr_14'] = tr.rolling(self.ATR_PERIOD).mean()
        df['atr_ratio'] = df['atr_14'] / df['close']

        # Bollinger Bands (20, 2)
        sma20 = df['close'].rolling(self.BB_PERIOD).mean()
        std20 = df['close'].rolling(self.BB_PERIOD).std()
        upper_bb = sma20 + (std20 * self.BB_STD)
        lower_bb = sma20 - (std20 * self.BB_STD)
        df['bollinger_pos'] = (df['close'] - lower_bb) / (upper_bb - lower_bb + 1e-9)
        df['bollinger_width'] = (upper_bb - lower_bb) / (sma20 + 1e-9)

        # Volume ratio
        df['volume_ratio_5d'] = df['volume'] / (df['volume'].rolling(5).mean() + 1e-9)

        # 1. On-Balance Volume (OBV) & 10-day OBV Momentum
        obv_direction = np.sign(df['close'].diff().fillna(0))
        obv = (obv_direction * df['volume']).cumsum()
        df['obv_10d_pct'] = obv.pct_change(10).fillna(0)

        # 2. Money Flow Index (MFI 14)
        typical_price = (df['high'] + df['low'] + df['close']) / 3.0
        money_flow = typical_price * df['volume']
        pos_flow = money_flow.where(typical_price > typical_price.shift(1), 0).rolling(14).sum()
        neg_flow = money_flow.where(typical_price < typical_price.shift(1), 0).rolling(14).sum()
        mfi = 100.0 - (100.0 / (1.0 + (pos_flow / (neg_flow + 1e-9))))
        df['mfi_14'] = mfi.fillna(50.0)

        # 3. 5-Day VWAP Ratio
        vwap_5d = (df['close'] * df['volume']).rolling(5).sum() / (df['volume'].rolling(5).sum() + 1e-9)
        df['vwap_ratio_5d'] = (df['close'] / vwap_5d) - 1.0

        # 4. Multi-Timeframe Trend Alignment (+1 Bullish, -1 Bearish, 0 Neutral)
        bullish_align = (df['ema_9_ratio'] > 0) & (df['ema_21_ratio'] > 0) & (df['return_10d'] > 0)
        bearish_align = (df['ema_9_ratio'] < 0) & (df['ema_21_ratio'] < 0) & (df['return_10d'] < 0)
        df['multi_timeframe_trend'] = np.where(bullish_align, 1, np.where(bearish_align, -1, 0))

        # Macro relative metrics
        if 'spy_close' in df.columns:
            df['spy_return_1d'] = df['spy_close'].pct_change(1)
            df['tsla_vs_spy_rel_strength'] = df['return_1d'] - df['spy_return_1d']

        if 'vix_close' in df.columns:
            df['vix_change_1d'] = df['vix_close'].pct_change(1)

        # Cross-Asset Divergence Features (detect when stock and market indicators diverge)
        if 'spy_close' in df.columns:
            spy_return_5d = df['spy_close'].pct_change(5)
            spy_return_10d = df['spy_close'].pct_change(10)
            df['tsla_spy_momentum_gap'] = df['return_5d'] - spy_return_5d
            df['tsla_spy_momentum_gap_10d'] = df['return_10d'] - spy_return_10d

        if 'vix_close' in df.columns:
            vix_change_5d = df['vix_close'].pct_change(5)
            # When stock rises but VIX also rises = warning signal (divergence)
            df['stock_vix_divergence'] = df['return_5d'] + vix_change_5d
            df['vix_regime'] = (df['vix_close'] > df['vix_close'].rolling(20).mean()).astype(int)

        return df

    def _add_event_catalyst_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transforms raw news sentiment into event-driven catalyst flags and lead-lag signals.
        Filters out raw noise by isolating significant sentiment surges & news catalyst events.
        
        Args:
            df: The dataframe containing features.
            
        Returns:
            The dataframe with news catalyst features added.
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
        Label mapping (for both 5% and 8% thresholds):
          2 -> Swing Up (Forward max price movement >= threshold)
          0 -> Swing Down (Forward min price movement <= -threshold)
          1 -> Neutral (No strong swing)
          
        Args:
            df: The dataframe.
            
        Returns:
            The dataframe with target columns added.
        """
        # Forward maximum return over next N days
        forward_max = df['high'].shift(-SWING_HORIZON_DAYS).rolling(SWING_HORIZON_DAYS).max()
        forward_max_return = (forward_max / df['close']) - 1.0

        # Forward minimum return over next N days
        forward_min = df['low'].shift(-SWING_HORIZON_DAYS).rolling(SWING_HORIZON_DAYS).min()
        forward_min_return = (forward_min / df['close']) - 1.0

        df['forward_max_return'] = forward_max_return
        df['forward_min_return'] = forward_min_return

        # 1. Standard 5% Swing Target
        targets_5 = np.full(len(df), 1) # default 1 = Neutral
        up_mask_5 = forward_max_return >= SWING_UP_THRESHOLD
        down_mask_5 = forward_min_return <= SWING_DOWN_THRESHOLD
        both_mask_5 = up_mask_5 & down_mask_5
        targets_5[up_mask_5] = 2
        targets_5[down_mask_5] = 0
        targets_5[both_mask_5] = np.where(forward_max_return[both_mask_5] > abs(forward_min_return[both_mask_5]), 2, 0)

        df['swing_target'] = targets_5
        df['swing_target_5pct'] = targets_5

        # 2. Strong 8% Swing Target
        targets_8 = np.full(len(df), 1)
        up_mask_8 = forward_max_return >= 0.08
        down_mask_8 = forward_min_return <= -0.08
        both_mask_8 = up_mask_8 & down_mask_8
        targets_8[up_mask_8] = 2
        targets_8[down_mask_8] = 0
        targets_8[both_mask_8] = np.where(forward_max_return[both_mask_8] > abs(forward_min_return[both_mask_8]), 2, 0)

        df['swing_target_8pct'] = targets_8
        return df

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    builder = FeatureBuilder()
    full_df = builder.build_dataset()
    logger.info("Class Distribution of Targets:")
    logger.info("\n" + str(full_df['swing_target'].value_counts()))
    logger.info("\nSample Columns:")
    logger.info("\n" + str(full_df[['close', 'return_1d', 'rsi_14', 'news_sentiment', 'political_trade_signal', 'x_sentiment_score', 'swing_target']].head()))
