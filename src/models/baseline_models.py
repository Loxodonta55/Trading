from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd

class BaselineClassifier:
    """
    Classic ML benchmark classifier suite (Logistic Regression, Decision Tree, Random Forest, Gradient Boosting)
    to rigorously compare TabFM foundation model performance against traditional old-school baselines.
    """
    def __init__(self, model_type: str = "rf"):
        self.model_type = model_type.lower()
        self.scaler = StandardScaler() if self.model_type == "logistic" else None
        
        if self.model_type == "logistic":
            self.model = LogisticRegression(max_iter=1000, C=0.1, random_state=42)
        elif self.model_type == "decision_tree":
            self.model = DecisionTreeClassifier(max_depth=3, random_state=42)
        elif self.model_type == "random_forest":
            self.model = RandomForestClassifier(n_estimators=100, max_depth=4, random_state=42)
        else: # Gradient Boosted Trees (HistGradientBoosting / XGBoost equivalent)
            self.model = HistGradientBoostingClassifier(
                max_iter=100,
                max_depth=4,
                learning_rate=0.05,
                random_state=42
            )

    def fit(self, X: pd.DataFrame, y: pd.Series):
        X_clean = X.fillna(0.0)
        if self.scaler:
            X_clean = self.scaler.fit_transform(X_clean)
        self.model.fit(X_clean, y)
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        X_clean = X.fillna(0.0)
        if self.scaler:
            X_clean = self.scaler.transform(X_clean)
            
        raw_probs = self.model.predict_proba(X_clean)
        classes = self.model.classes_
        
        full_probs = np.zeros((len(X), 3))
        for i, c in enumerate(classes):
            if c in [0, 1, 2]:
                full_probs[:, int(c)] = raw_probs[:, i]
        return full_probs

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        probs = self.predict_proba(X)
        return np.argmax(probs, axis=1)
