import pytest
import pandas as pd
import numpy as np
from src.backtest.engine import WalkForwardBacktester

def test_calculate_metrics_positive_returns():
    # Arrange
    tester = WalkForwardBacktester()
    df = pd.DataFrame({
        'strategy_return': [0.01, 0.02, 0.01],
        'equity_curve': [1.01, 1.0302, 1.0405],
        'buy_hold_equity': [1.01, 1.02, 1.03],
        'action': [1, 1, 0]
    })
    
    # Act
    metrics = tester._calculate_metrics(df)
    
    # Assert
    assert metrics['total_return'] > 0

def test_calculate_metrics_zero_trades():
    # Arrange
    tester = WalkForwardBacktester()
    df = pd.DataFrame({
        'strategy_return': [0.0, 0.0, 0.0],
        'equity_curve': [1.0, 1.0, 1.0],
        'buy_hold_equity': [1.0, 1.0, 1.0],
        'action': [0, 0, 0]
    })
    
    # Act
    metrics = tester._calculate_metrics(df)
    
    # Assert
    assert metrics['n_trades'] == 0

def test_calculate_metrics_sharpe_ratio():
    # Arrange
    tester = WalkForwardBacktester()
    df = pd.DataFrame({
        'strategy_return': [0.01, 0.01, 0.01],
        'equity_curve': [1.01, 1.02, 1.03],
        'buy_hold_equity': [1.0, 1.0, 1.0],
        'action': [1, 1, 1]
    })
    
    # Act
    metrics = tester._calculate_metrics(df)
    
    # Assert
    assert 'sharpe_ratio' in metrics
    assert not np.isnan(metrics['sharpe_ratio'])

def test_calculate_metrics_max_drawdown():
    # Arrange
    tester = WalkForwardBacktester()
    df = pd.DataFrame({
        'strategy_return': [-0.01, -0.01, 0.0],
        'equity_curve': [0.99, 0.98, 0.98],
        'buy_hold_equity': [1.0, 1.0, 1.0],
        'action': [1, 1, 1]
    })
    
    # Act
    metrics = tester._calculate_metrics(df)
    
    # Assert
    assert 'max_drawdown' in metrics
    assert metrics['max_drawdown'] <= 0

def test_backtest_initialization_defaults():
    # Arrange & Act
    tester = WalkForwardBacktester()
    
    # Assert
    assert hasattr(tester, 'stop_loss')
    assert hasattr(tester, 'take_profit')
