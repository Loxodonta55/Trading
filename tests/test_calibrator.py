import pytest
from src.features.calibrator import FeatureCalibrator

def test_calibrate_returns_top_k_features(sample_features_df):
    # Arrange
    calibrator = FeatureCalibrator(top_k=2)
    
    # Act
    # Assuming 'target_label' exists in sample_features_df for training purposes
    if 'target_label' not in sample_features_df.columns:
        sample_features_df['target_label'] = 0
    
    features, importance = calibrator.calibrate(sample_features_df, 'target_label')
    
    # Assert
    assert len(features) == 2

def test_calibrate_returns_importance_series(sample_features_df):
    # Arrange
    calibrator = FeatureCalibrator(top_k=2)
    
    # Act
    if 'target_label' not in sample_features_df.columns:
        sample_features_df['target_label'] = 0
        
    features, importance = calibrator.calibrate(sample_features_df, 'target_label')
    
    # Assert
    assert hasattr(importance, 'index')
    assert len(importance) >= 2

def test_calibrate_feature_names_are_strings(sample_features_df):
    # Arrange
    calibrator = FeatureCalibrator(top_k=2)
    
    # Act
    if 'target_label' not in sample_features_df.columns:
        sample_features_df['target_label'] = 0
        
    features, importance = calibrator.calibrate(sample_features_df, 'target_label')
    
    # Assert
    for f in features:
        assert isinstance(f, str)
