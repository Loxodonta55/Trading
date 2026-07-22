from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
import numpy as np
import pandas as pd

class BaselineClassifier:
    """
    Classic ML benchmark classifier to compare TabFM performance against.
    """
    def __init__(self, model_type: str = "rf"):
        self.model_type = model_type
        self.model = HistGradientBoostingClassifier(
            max_iter=100,
            max_depth=4,
            learning_rate=0.05,
            random_state=42
        )

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        raw_probs = self.model.predict_proba(X)
        classes = self.model.classes_
        
        full_probs = np.zeros((len(X), 3))
        for i, c in enumerate(classes):
            if c in [0, 1, 2]:
                full_probs[:, int(c)] = raw_probs[:, i]
        return full_probs

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        probs = self.predict_proba(X)
        return np.argmax(probs, axis=1)
