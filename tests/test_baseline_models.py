import pytest
import numpy as np
from src.models.baseline_models import BaselineClassifier

@pytest.fixture
def synthetic_data():
    X = np.random.rand(100, 5)
    y = np.random.choice([0, 1, 2], size=100)
    return X, y

def test_random_forest_fit_predict(synthetic_data):
    # Arrange
    X, y = synthetic_data
    model = BaselineClassifier(model_type='rf')
    
    # Act
    model.fit(X, y)
    preds = model.predict(X)
    
    # Assert
    assert set(preds).issubset({0, 1, 2})
    assert len(preds) == len(y)

def test_logistic_regression_fit_predict(synthetic_data):
    # Arrange
    X, y = synthetic_data
    model = BaselineClassifier(model_type='lr')
    
    # Act
    model.fit(X, y)
    preds = model.predict(X)
    
    # Assert
    assert set(preds).issubset({0, 1, 2})

def test_gbm_fit_predict(synthetic_data):
    # Arrange
    X, y = synthetic_data
    model = BaselineClassifier(model_type='gbm')
    
    # Act
    model.fit(X, y)
    preds = model.predict(X)
    
    # Assert
    assert set(preds).issubset({0, 1, 2})

def test_predict_proba_shape(synthetic_data):
    # Arrange
    X, y = synthetic_data
    model = BaselineClassifier(model_type='rf')
    
    # Act
    model.fit(X, y)
    probs = model.predict_proba(X)
    
    # Assert
    assert probs.shape == (len(X), 3)

def test_predict_proba_sums_to_one(synthetic_data):
    # Arrange
    X, y = synthetic_data
    model = BaselineClassifier(model_type='rf')
    
    # Act
    model.fit(X, y)
    probs = model.predict_proba(X)
    
    # Assert
    assert np.allclose(probs.sum(axis=1), 1.0)

def test_single_class_handling():
    # Arrange
    X = np.random.rand(50, 5)
    y = np.zeros(50)  # All class 0
    model = BaselineClassifier(model_type='rf')
    
    # Act
    model.fit(X, y)
    preds = model.predict(X)
    
    # Assert
    assert len(preds) == len(y)
    assert set(preds) == {0}
