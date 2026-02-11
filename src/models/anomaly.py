from sklearn.ensemble import IsolationForest
import numpy as np
import pickle
import os

class AnomalyDetector:
    """
    Wrapper for Anomaly Detection using Isolation Forest.
    """
    def __init__(self, contamination=0.01):
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.is_fitted = False

    def train(self, X):
        """
        Train the isolation forest on historical features.
        """
        print("Training Anomaly Detector...")
        self.model.fit(X)
        self.is_fitted = True

    def score(self, features_array):
        """
        Return anomaly score. 
        Isolation Forest returns logical decision function (lower is more anomalous).
        We invert/normalize it to [0, 1] risk score roughly.
        """
        if not self.is_fitted:
            return 0.5 # Default uncertainty
        
        # decision_function: average anomaly score of X of the base classifiers.
        # The anomaly score of an input sample is computed as the mean anomaly score of the trees in the forest.
        # The measure of normality of an observation given a tree is the depth of the leaf containing this observation, 
        # which is equivalent to the number of splittings required to isolate this point.
        # In case of several observations n_left in the leaf, the average path length of a n_left samples isolation tree is added.
        
        scores = self.model.decision_function(features_array)
        # decision_function returns negative for outliers, positive for inliers.
        # Range theoretically unbounded but mostly within [-0.5, 0.5] for standardized data.
        
        # Simple normalization for risk: 
        # Deep negative -> High Risk (1.0)
        # Positive -> Low Risk (0.0)
        
        risk_scores = 1 / (1 + np.exp(scores)) # Sigmoid-ish
        return risk_scores

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)
            
    def load(self, path):
        if os.path.exists(path):
            with open(path, 'rb') as f:
                self.model = pickle.load(f)
            self.is_fitted = True
