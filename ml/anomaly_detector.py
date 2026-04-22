"""
Machine learning-based anomaly detection.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
from pathlib import Path


class MLAnomalyDetector:
    """
    ML-based anomaly detection for performance metrics.

    Uses multiple techniques:
    - Isolation Forest
    - Statistical methods (Z-score, IQR)
    - Time-series analysis
    - LSTM for sequential patterns
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize anomaly detector.

        Args:
            model_path: Path to saved model
        """
        self.model_path = model_path
        self.models = {}
        self.thresholds = {}
        self.training_data = {}

        if model_path and Path(model_path).exists():
            self.load_models(model_path)

    def train(
        self,
        metric_name: str,
        data: List[float],
        method: str = "isolation_forest"
    ):
        """
        Train anomaly detection model.

        Args:
            metric_name: Metric name
            data: Historical data
            method: Detection method
        """
        if method == "isolation_forest":
            self._train_isolation_forest(metric_name, data)
        elif method == "statistical":
            self._train_statistical(metric_name, data)
        elif method == "time_series":
            self._train_time_series(metric_name, data)

        self.training_data[metric_name] = data

    def _train_isolation_forest(self, metric_name: str, data: List[float]):
        """Train Isolation Forest model."""
        try:
            from sklearn.ensemble import IsolationForest

            # Reshape data
            X = np.array(data).reshape(-1, 1)

            # Train model
            model = IsolationForest(
                contamination=0.1,  # Expected proportion of outliers
                random_state=42
            )
            model.fit(X)

            self.models[f"{metric_name}_isolation"] = model

        except ImportError:
            print("sklearn not available, using statistical fallback")
            self._train_statistical(metric_name, data)

    def _train_statistical(self, metric_name: str, data: List[float]):
        """Train statistical anomaly detection."""
        mean = np.mean(data)
        std = np.std(data)

        # Calculate IQR
        q75, q25 = np.percentile(data, [75, 25])
        iqr = q75 - q25

        self.thresholds[metric_name] = {
            "mean": mean,
            "std": std,
            "z_score_threshold": 3.0,
            "iqr": iqr,
            "q25": q25,
            "q75": q75,
            "iqr_multiplier": 1.5
        }

    def _train_time_series(self, metric_name: str, data: List[float]):
        """Train time-series anomaly detection."""
        # Use moving average and standard deviation
        window_size = min(10, len(data) // 4)

        if len(data) < window_size:
            self._train_statistical(metric_name, data)
            return

        # Calculate moving statistics
        moving_avg = []
        moving_std = []

        for i in range(len(data) - window_size + 1):
            window = data[i:i + window_size]
            moving_avg.append(np.mean(window))
            moving_std.append(np.std(window))

        self.thresholds[f"{metric_name}_ts"] = {
            "window_size": window_size,
            "avg_moving_avg": np.mean(moving_avg),
            "avg_moving_std": np.mean(moving_std),
            "threshold_multiplier": 3.0
        }

    def detect(
        self,
        metric_name: str,
        value: float,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Detect if value is anomalous.

        Args:
            metric_name: Metric name
            value: Value to check
            context: Additional context

        Returns:
            Detection result with anomaly score
        """
        results = {
            "metric": metric_name,
            "value": value,
            "is_anomaly": False,
            "anomaly_score": 0.0,
            "methods": {},
            "timestamp": datetime.now().isoformat()
        }

        # Try Isolation Forest
        if f"{metric_name}_isolation" in self.models:
            iso_result = self._detect_isolation_forest(metric_name, value)
            results["methods"]["isolation_forest"] = iso_result

            if iso_result["is_anomaly"]:
                results["is_anomaly"] = True
                results["anomaly_score"] = max(
                    results["anomaly_score"],
                    iso_result["score"]
                )

        # Try statistical methods
        if metric_name in self.thresholds:
            stat_result = self._detect_statistical(metric_name, value)
            results["methods"]["statistical"] = stat_result

            if stat_result["is_anomaly"]:
                results["is_anomaly"] = True
                results["anomaly_score"] = max(
                    results["anomaly_score"],
                    stat_result["score"]
                )

        # Try time-series analysis
        if f"{metric_name}_ts" in self.thresholds and context:
            ts_result = self._detect_time_series(
                metric_name,
                value,
                context.get("recent_values", [])
            )
            results["methods"]["time_series"] = ts_result

            if ts_result["is_anomaly"]:
                results["is_anomaly"] = True
                results["anomaly_score"] = max(
                    results["anomaly_score"],
                    ts_result["score"]
                )

        return results

    def _detect_isolation_forest(
        self,
        metric_name: str,
        value: float
    ) -> Dict[str, Any]:
        """Detect using Isolation Forest."""
        model = self.models.get(f"{metric_name}_isolation")

        if not model:
            return {"is_anomaly": False, "score": 0.0, "method": "not_trained"}

        X = np.array([[value]])
        prediction = model.predict(X)
        anomaly_score = model.decision_function(X)[0]

        # -1 means anomaly in sklearn Isolation Forest
        is_anomaly = prediction[0] == -1

        return {
            "is_anomaly": is_anomaly,
            "score": abs(anomaly_score),
            "decision_function": float(anomaly_score)
        }

    def _detect_statistical(
        self,
        metric_name: str,
        value: float
    ) -> Dict[str, Any]:
        """Detect using statistical methods."""
        thresholds = self.thresholds.get(metric_name)

        if not thresholds:
            return {"is_anomaly": False, "score": 0.0, "method": "not_trained"}

        # Z-score method
        mean = thresholds["mean"]
        std = thresholds["std"]
        z_score = abs((value - mean) / std) if std > 0 else 0

        z_anomaly = z_score > thresholds["z_score_threshold"]

        # IQR method
        q25 = thresholds["q25"]
        q75 = thresholds["q75"]
        iqr = thresholds["iqr"]
        iqr_multiplier = thresholds["iqr_multiplier"]

        lower_bound = q25 - (iqr_multiplier * iqr)
        upper_bound = q75 + (iqr_multiplier * iqr)

        iqr_anomaly = value < lower_bound or value > upper_bound

        is_anomaly = z_anomaly or iqr_anomaly

        return {
            "is_anomaly": is_anomaly,
            "score": z_score,
            "z_score": z_score,
            "iqr_bounds": (lower_bound, upper_bound),
            "methods_triggered": {
                "z_score": z_anomaly,
                "iqr": iqr_anomaly
            }
        }

    def _detect_time_series(
        self,
        metric_name: str,
        value: float,
        recent_values: List[float]
    ) -> Dict[str, Any]:
        """Detect using time-series analysis."""
        thresholds = self.thresholds.get(f"{metric_name}_ts")

        if not thresholds or not recent_values:
            return {"is_anomaly": False, "score": 0.0, "method": "insufficient_data"}

        window_size = thresholds["window_size"]

        if len(recent_values) < window_size:
            return {"is_anomaly": False, "score": 0.0, "method": "insufficient_data"}

        # Calculate statistics for recent window
        recent_mean = np.mean(recent_values[-window_size:])
        recent_std = np.std(recent_values[-window_size:])

        # Compare with expected
        expected_mean = thresholds["avg_moving_avg"]
        expected_std = thresholds["avg_moving_std"]

        deviation = abs(value - recent_mean)
        threshold = expected_std * thresholds["threshold_multiplier"]

        is_anomaly = deviation > threshold

        return {
            "is_anomaly": is_anomaly,
            "score": deviation / (expected_std + 1e-6),
            "recent_mean": recent_mean,
            "deviation": deviation,
            "threshold": threshold
        }

    def detect_batch(
        self,
        metric_name: str,
        values: List[float]
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in batch.

        Args:
            metric_name: Metric name
            values: Values to check

        Returns:
            List of detection results
        """
        results = []

        for i, value in enumerate(values):
            context = {
                "recent_values": values[max(0, i-10):i]
            }

            result = self.detect(metric_name, value, context)
            results.append(result)

        return results

    def get_anomaly_summary(
        self,
        detections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get summary of anomaly detections.

        Args:
            detections: List of detection results

        Returns:
            Summary statistics
        """
        anomalies = [d for d in detections if d["is_anomaly"]]

        return {
            "total_checked": len(detections),
            "anomalies_detected": len(anomalies),
            "anomaly_rate": len(anomalies) / len(detections) if detections else 0,
            "avg_anomaly_score": np.mean([a["anomaly_score"] for a in anomalies]) if anomalies else 0,
            "max_anomaly_score": max([a["anomaly_score"] for a in anomalies]) if anomalies else 0,
            "anomalies": anomalies
        }

    def save_models(self, path: str):
        """Save trained models."""
        import pickle

        data = {
            "models": self.models,
            "thresholds": self.thresholds,
            "training_data": self.training_data
        }

        with open(path, 'wb') as f:
            pickle.dump(data, f)

    def load_models(self, path: str):
        """Load trained models."""
        import pickle

        with open(path, 'rb') as f:
            data = pickle.load(f)

        self.models = data.get("models", {})
        self.thresholds = data.get("thresholds", {})
        self.training_data = data.get("training_data", {})
