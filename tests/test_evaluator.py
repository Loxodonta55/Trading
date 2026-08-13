import pytest
from src.analysis.evaluator import SensitivityEvaluator

def test_evaluator_initialization():
    # Arrange & Act
    evaluator = SensitivityEvaluator()
    
    # Assert
    assert hasattr(evaluator, 'calibrator')
    assert hasattr(evaluator, 'backtester')

def test_evaluator_confidence_threshold():
    # Arrange & Act
    evaluator = SensitivityEvaluator(confidence_threshold=0.6)
    
    # Assert
    assert evaluator.confidence_threshold == 0.6
