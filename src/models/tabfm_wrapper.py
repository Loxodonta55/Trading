import logging
import numpy as np
import pandas as pd
from typing import Optional, Union, Dict, Self
from sklearn.base import BaseEstimator, ClassifierMixin

import torch

logger = logging.getLogger(__name__)

_SHARED_TABFM_MODEL = None
_SHARED_TABFM_CLASSIFIER = None

class TabFMWrapper(BaseEstimator, ClassifierMixin):
    """
    Wrapper for Google's Tabular Foundation Model (TabFM).
    Supports zero-shot and in-context classification for tabular stock features.
    Provides scikit-learn compatible fit() and predict_proba() methods.
    """
    def __init__(self, model_type: str = "classification") -> None:
        """
        Initializes the TabFMWrapper.

        Args:
            model_type: The model type ("classification").
        """
        self.model_type = model_type
        self.tabfm_model = None
        self.fallback_model = None
        self.is_tabfm_available = False
        self._is_fallback = False
        self.classes_ = np.array([0, 1, 2]) # 0: Swing Down, 1: Neutral, 2: Swing Up
        
        self._initialize_tabfm()

    @property
    def is_fallback(self) -> bool:
        """Indicates if the fallback model is being used."""
        return self._is_fallback

    def _initialize_tabfm(self) -> None:
        """Attempts to load google tabfm model, setting fallback if unavailable."""
        global _SHARED_TABFM_CLASSIFIER
        if _SHARED_TABFM_CLASSIFIER is not None:
            self.tabfm_model = _SHARED_TABFM_CLASSIFIER
            self.is_tabfm_available = True
            return

        try:
            from tabfm import TabFMClassifier, tabfm_v1_0_0_pytorch
            logger.info("[TabFMWrapper] Loading Google TabFM model weights...")
            model = tabfm_v1_0_0_pytorch.load(model_type=self.model_type, dtype=torch.float16)
            self.tabfm_model = TabFMClassifier(model=model)
            _SHARED_TABFM_CLASSIFIER = self.tabfm_model
            self.is_tabfm_available = True
            logger.info("[TabFMWrapper] Google TabFM model successfully loaded!")
        except Exception as e:
            logger.info(f"[TabFMWrapper] TabFM native load info/fallback: {e}")
            logger.info("[TabFMWrapper] Using Gradient Boosted In-Context Classifier for Tabular Zero-Shot baseline...")
            logger.warning('TabFM unavailable, using RandomForest fallback. Results labeled as TabFM are actually RF.')
            self._is_fallback = True
            from sklearn.ensemble import RandomForestClassifier
            self.fallback_model = RandomForestClassifier(
                n_estimators=30,
                max_depth=6,
                random_state=42,
                n_jobs=1
            )

    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]) -> Self:
        """
        Passes training context to TabFM or trains baseline.
        
        Args:
            X: Training features.
            y: Training labels.
            
        Returns:
            Self.
        """
        if self.is_tabfm_available:
            self.tabfm_model.fit(X, y)
        else:
            self.fallback_model.fit(X, y)
        return self

    def predict_proba(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """
        Returns class probabilities [P(Down), P(Neutral), P(Up)].
        
        Args:
            X: Input features.
            
        Returns:
            An array of probabilities.
        """
        if self.is_tabfm_available:
            return self.tabfm_model.predict_proba(X)
        else:
            raw_probs = self.fallback_model.predict_proba(X)
            classes = self.fallback_model.classes_
            
            # Map raw probabilities to standardized 3-class array [P(0=Down), P(1=Neutral), P(2=Up)]
            full_probs = np.zeros((len(X), 3))
            for i, c in enumerate(classes):
                if c in [0, 1, 2]:
                    full_probs[:, int(c)] = raw_probs[:, i]
            return full_probs

    def predict(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """
        Predicts class label with highest probability.
        
        Args:
            X: Input features.
            
        Returns:
            An array of predicted labels.
        """
        probs = self.predict_proba(X)
        return np.argmax(probs, axis=1)
