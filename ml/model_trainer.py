"""
Model training utilities for ML-based features.
"""

from typing import Dict, List, Any
from pathlib import Path


class ModelTrainer:
    """
    Trains and manages ML models for performance analysis.
    """

    def __init__(self, models_dir: str = "./models"):
        """
        Initialize model trainer.

        Args:
            models_dir: Directory to save trained models
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def train_anomaly_models(
        self,
        historical_data: Dict[str, List[float]],
        method: str = "isolation_forest"
    ) -> Dict[str, Any]:
        """
        Train anomaly detection models for all metrics.

        Args:
            historical_data: Dictionary of metric_name -> values
            method: Detection method

        Returns:
            Training results
        """
        from .anomaly_detector import MLAnomalyDetector

        detector = MLAnomalyDetector()
        results = {}

        for metric_name, data in historical_data.items():
            if len(data) < 30:  # Need minimum data
                results[metric_name] = {
                    "status": "insufficient_data",
                    "samples": len(data)
                }
                continue

            detector.train(metric_name, data, method=method)

            results[metric_name] = {
                "status": "trained",
                "samples": len(data),
                "method": method
            }

        # Save models
        model_path = self.models_dir / "anomaly_detector.pkl"
        detector.save_models(str(model_path))

        return {
            "trained_metrics": list(results.keys()),
            "results": results,
            "model_path": str(model_path)
        }

    def train_prediction_models(
        self,
        historical_data: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Train prediction models for all metrics.

        Args:
            historical_data: Dictionary of metric_name -> time series data

        Returns:
            Training results
        """
        from .predictor import PerformancePredictor

        predictor = PerformancePredictor()
        results = {}

        for metric_name, data in historical_data.items():
            if len(data) < 10:
                results[metric_name] = {
                    "status": "insufficient_data",
                    "samples": len(data)
                }
                continue

            predictor.train(metric_name, data)

            results[metric_name] = {
                "status": "trained",
                "samples": len(data)
            }

        return {
            "trained_metrics": list(results.keys()),
            "results": results
        }

    def evaluate_model_performance(
        self,
        metric_name: str,
        test_data: List[float],
        model_type: str = "anomaly"
    ) -> Dict[str, Any]:
        """
        Evaluate model performance.

        Args:
            metric_name: Metric name
            test_data: Test data
            model_type: Type of model (anomaly or prediction)

        Returns:
            Evaluation metrics
        """
        if model_type == "anomaly":
            return self._evaluate_anomaly_model(metric_name, test_data)
        elif model_type == "prediction":
            return self._evaluate_prediction_model(metric_name, test_data)

        return {"error": "Unknown model type"}

    def _evaluate_anomaly_model(
        self,
        metric_name: str,
        test_data: List[float]
    ) -> Dict[str, Any]:
        """Evaluate anomaly detection model."""
        from .anomaly_detector import MLAnomalyDetector

        model_path = self.models_dir / "anomaly_detector.pkl"

        if not model_path.exists():
            return {"error": "Model not found"}

        detector = MLAnomalyDetector(str(model_path))
        detections = detector.detect_batch(metric_name, test_data)
        summary = detector.get_anomaly_summary(detections)

        return {
            "metric": metric_name,
            "test_samples": len(test_data),
            "anomalies_detected": summary["anomalies_detected"],
            "anomaly_rate": summary["anomaly_rate"],
            "avg_anomaly_score": summary["avg_anomaly_score"]
        }

    def _evaluate_prediction_model(
        self,
        metric_name: str,
        test_data: List[float]
    ) -> Dict[str, Any]:
        """Evaluate prediction model."""
        # Would implement prediction accuracy metrics
        return {
            "metric": metric_name,
            "test_samples": len(test_data),
            "status": "not_implemented"
        }
