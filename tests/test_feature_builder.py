import pytest
import pandas as pd
import numpy as np
from src.features.builder import FeatureBuilder

def test_add_technical_features_rsi(sample_price_df):
    # Arrange
    builder = FeatureBuilder.__new__(FeatureBuilder)
    
    # Act
    result = builder._add_technical_features(sample_price_df.copy())
    
    # Assert
    assert 'rsi' in result.columns
    assert result['rsi'].min() >= 0.0
    assert result['rsi'].max() <= 100.0

def test_add_technical_features_macd(sample_price_df):
    # Arrange
    builder = FeatureBuilder.__new__(FeatureBuilder)
    
    # Act
    result = builder._add_technical_features(sample_price_df.copy())
    
    # Assert
    assert 'macd' in result.columns
    assert 'macd_signal' in result.columns
    assert 'macd_hist' in result.columns

def test_add_technical_features_bollinger(sample_price_df):
    # Arrange
    builder = FeatureBuilder.__new__(FeatureBuilder)
    
    # Act
    result = builder._add_technical_features(sample_price_df.copy())
    
    # Assert
    assert 'bb_pos' in result.columns

def test_add_technical_features_atr(sample_price_df):
    # Arrange
    builder = FeatureBuilder.__new__(FeatureBuilder)
    
    # Act
    result = builder._add_technical_features(sample_price_df.copy())
    
    # Assert
    assert 'atr' in result.columns
    assert result['atr'].min() >= 0.0

def test_add_technical_features_volume_ratio(sample_price_df):
    # Arrange
    builder = FeatureBuilder.__new__(FeatureBuilder)
    
    # Act
    result = builder._add_technical_features(sample_price_df.copy())
    
    # Assert
    assert 'vol_ratio_5d' in result.columns

def test_add_swing_targets(sample_price_df):
    # Arrange
    builder = FeatureBuilder.__new__(FeatureBuilder)
    
    # Act
    result = builder._add_swing_targets(sample_price_df.copy())
    
    # Assert
    assert 'target_label' in result.columns
    assert set(result['target_label'].dropna().unique()).issubset({0, 1, 2})

def test_add_swing_targets_distribution(sample_price_df):
    # Arrange
    builder = FeatureBuilder.__new__(FeatureBuilder)
    df = sample_price_df.copy()
    
    # create synthetic data with large swings to ensure all classes
    # Assuming daily data index
    if len(df) > 20:
        df.loc[df.index[0:10], 'close'] = np.linspace(100, 150, 10)  # Uptrend
        df.loc[df.index[10:20], 'close'] = np.linspace(150, 80, 10)   # Downtrend
    
    # Act
    result = builder._add_swing_targets(df)
    
    # Assert
    labels = result['target_label'].dropna().unique()
    assert len(labels) > 0 # At least one class generated
    
def test_add_event_catalyst_features(sample_price_df):
    # Arrange
    builder = FeatureBuilder.__new__(FeatureBuilder)
    df = sample_price_df.copy()
    df['news_sentiment'] = 0.5
    
    # Act
    result = builder._add_event_catalyst_features(df)
    
    # Assert
    assert 'has_catalyst' in result.columns
