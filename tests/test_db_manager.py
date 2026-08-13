import pytest
import pandas as pd
from src.data.db_manager import DatabaseManager

def test_init_creates_tables(temp_db_path):
    # Arrange & Act
    db = DatabaseManager(db_path=temp_db_path)
    
    # Assert
    assert db.db_path == temp_db_path

def test_save_and_load_features(temp_db_path, sample_features_df):
    # Arrange
    db = DatabaseManager(db_path=temp_db_path)
    ticker = "TEST"
    
    # Act
    db.save_features(ticker, sample_features_df)
    loaded = db.load_features(ticker)
    
    # Assert
    assert not loaded.empty
    assert len(loaded) == len(sample_features_df)

def test_save_features_upsert(temp_db_path, sample_features_df):
    # Arrange
    db = DatabaseManager(db_path=temp_db_path)
    ticker = "TEST"
    
    # Act
    db.save_features(ticker, sample_features_df)
    db.save_features(ticker, sample_features_df)  # Save again
    loaded = db.load_features(ticker)
    
    # Assert
    assert len(loaded) == len(sample_features_df)

def test_metadata_get_set(temp_db_path):
    # Arrange
    db = DatabaseManager(db_path=temp_db_path)
    key = "test_key"
    value = "test_value"
    
    # Act
    db.set_metadata(key, value)
    result = db.get_metadata(key)
    
    # Assert
    assert result == value

def test_get_last_data_date_empty(temp_db_path):
    # Arrange
    db = DatabaseManager(db_path=temp_db_path)
    
    # Act
    result = db.get_last_data_date("UNKNOWN")
    
    # Assert
    assert result is None

def test_set_and_get_last_data_date(temp_db_path):
    # Arrange
    db = DatabaseManager(db_path=temp_db_path)
    ticker = "TEST"
    date = "2023-01-01"
    
    # Act
    db.set_last_data_date(ticker, date)
    result = db.get_last_data_date(ticker)
    
    # Assert
    assert result == date
