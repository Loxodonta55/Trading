import logging
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
from typing import Self

logger = logging.getLogger(__name__)

class BaselineClassifier:
    """
    Classic ML benchmark classifier suite (Logistic Regression, Decision Tree, Random Forest, Gradient Boosting)
    to rigorously compare TabFM foundation model performance against traditional old-school baselines.
    """
    DEFAULT_N_ESTIMATORS = 100
    DEFAULT_MAX_DEPTH = 4
    DEFAULT_LEARNING_RATE = 0.05
    RANDOM_STATE = 42

    def __init__(self, model_type: str = "rf") -> None:
        """
        Initializes a baseline classifier.

        Args:
            model_type: The type of baseline model to use.
        """
        self.model_type = model_type.lower()
        self.scaler = StandardScaler() if self.model_type == "logistic" else None
        
        if self.model_type == "logistic":
            self.model = LogisticRegression(max_iter=1000, C=0.1, random_state=self.RANDOM_STATE)
        elif self.model_type == "decision_tree":
            self.model = DecisionTreeClassifier(max_depth=3, random_state=self.RANDOM_STATE)
        elif self.model_type == "random_forest":
            self.model = RandomForestClassifier(
                n_estimators=self.DEFAULT_N_ESTIMATORS, 
                max_depth=self.DEFAULT_MAX_DEPTH, 
                random_state=self.RANDOM_STATE
            )
        else: # Gradient Boosted Trees (HistGradientBoosting / XGBoost equivalent)
            self.model = HistGradientBoostingClassifier(
                max_iter=100,
                max_depth=self.DEFAULT_MAX_DEPTH,
                learning_rate=self.DEFAULT_LEARNING_RATE,
                random_state=self.RANDOM_STATE
            )

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Self:
        """
        Fits the baseline model to the given data.

        Args:
            X: Training features.
            y: Training labels.
            
        Returns:
            Self.
        """
        self._single_class = None
        if len(y.unique()) <= 1:
            self._single_class = y.iloc[0] if len(y) > 0 else 0
            return self

        X_clean = X.fillna(0.0)
        if self.scaler:
            X_clean = self.scaler.fit_transform(X_clean)
        self.model.fit(X_clean, y)
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predicts class probabilities for the input data.

        Args:
            X: Input features.

        Returns:
            An array of class probabilities (shape: n_samples, 3).
        """
        X_clean = X.fillna(0.0)
        n_samples = len(X)

        if getattr(self, '_single_class', None) is not None:
            full_probs = np.zeros((n_samples, 3))
            c = int(self._single_class)
            if c in [0, 1, 2]:
                full_probs[:, c] = 1.0
            return full_probs

        if self.scaler:
            X_clean = self.scaler.transform(X_clean)
            
        raw_probs = self.model.predict_proba(X_clean)
        classes = self.model.classes_
        
        full_probs = np.zeros((n_samples, 3))
        for i, c in enumerate(classes):
            if c in [0, 1, 2]:
                full_probs[:, int(c)] = raw_probs[:, i]
        return full_probs

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predicts the class labels for the input data.

        Args:
            X: Input features.

        Returns:
            An array of predicted class labels.
        """
        probs = self.predict_proba(X)
        return np.argmax(probs, axis=1)
