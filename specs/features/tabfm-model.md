# 📋 Feature Spec: Google TabFM Predictive Engine & Baselines

---

## 📌 Status
- **Status**: Implemented / In Re-engineering
- **Module**: `src/models/` & `.tabfm_src/`
- **Re-engineered Components**: `tabfm_wrapper.py`, `baseline_models.py`, Google TabFM Submodule

---

## 🎯 Zweck & Funktionalität
Einsatz des **Google TabFM Foundation Models** zur Analyse tabulärer Zeitreihenfeatures und Vorhersage von Swing-Wendepunkten. Stets Nutzung der aktuellsten Version von TabFM mit Vergleich gegen Baseline-Modelle.

---

## 🏗️ Spezifizierte Komponenten

### 1. Google TabFM Wrapper (`tabfm_wrapper.py`)
- **Modell-Integration**: Direkter Import des Google TabFM Frameworks aus `.tabfm_src` (oder aktueller PyPI-Version).
- **Zero-Shot / Few-Shot Fine-Tuning**: Verwertung von Kontext-Beispielen aus der Finanzhistorie.
- **Output**: Vorhersagewahrscheinlichkeiten `prob_up` (Wahrscheinlichkeit für bullischen Swing) und `prob_down`.

### 2. Baseline Modelle & Ablation Benchmark (`baseline_models.py`)
- **Vergleichsmodelle**: LightGBM, Logistic Regression, Random Forest.
- **Funktion**: Automatische Gegenüberstellung, um den Mehrwert (Alpha) von Google TabFM gegenüber klassischen ML-Verfahren zu belegen.
