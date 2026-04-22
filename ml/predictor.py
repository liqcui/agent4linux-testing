"""
Performance prediction using machine learning.
"""

import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


class PerformancePredictor:
    """
    Predicts future performance metrics using machine learning.
    """

    def __init__(self):
        """Initialize predictor."""
        self.models = {}
        self.scalers = {}

    def train(
        self,
        metric_name: str,
        historical_data: List[Dict[str, Any]],
        features: Optional[List[str]] = None
    ):
        """
        Train prediction model.

        Args:
            metric_name: Metric to predict
            historical_data: Historical data with timestamps and values
            features: Feature names for prediction
        """
        try:
            from sklearn.linear_model import LinearRegression
            from sklearn.preprocessing import StandardScaler

            # Extract features and targets
            X, y = self._prepare_data(historical_data, metric_name, features)

            if len(X) < 10:
                print(f"Insufficient data for {metric_name}, need at least 10 samples")
                return

            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Train model
            model = LinearRegression()
            model.fit(X_scaled, y)

            self.models[metric_name] = model
            self.scalers[metric_name] = scaler

        except ImportError:
            print("sklearn not available, predictions disabled")

    def _prepare_data(
        self,
        data: List[Dict[str, Any]],
        metric_name: str,
        features: Optional[List[str]]
    ) -> tuple:
        """Prepare training data."""
        X = []
        y = []

        for i, entry in enumerate(data):
            # Use time index as basic feature
            features_vec = [i]

            # Add custom features if provided
            if features:
                for feature in features:
                    features_vec.append(entry.get(feature, 0))

            X.append(features_vec)
            y.append(entry.get(metric_name, 0))

        return np.array(X), np.array(y)

    def predict(
        self,
        metric_name: str,
        steps_ahead: int = 1,
        features: Optional[Dict[str, Any]] = None
    ) -> List[float]:
        """
        Predict future values.

        Args:
            metric_name: Metric to predict
            steps_ahead: Number of steps to predict
            features: Feature values for prediction

        Returns:
            List of predicted values
        """
        model = self.models.get(metric_name)
        scaler = self.scalers.get(metric_name)

        if not model or not scaler:
            return []

        predictions = []

        for step in range(steps_ahead):
            # Prepare features
            feature_vec = [step]

            if features:
                for value in features.values():
                    feature_vec.append(value)

            # Scale and predict
            X = scaler.transform([feature_vec])
            pred = model.predict(X)[0]

            predictions.append(pred)

        return predictions

    def predict_with_confidence(
        self,
        metric_name: str,
        steps_ahead: int = 1
    ) -> List[Dict[str, float]]:
        """
        Predict with confidence intervals.

        Args:
            metric_name: Metric to predict
            steps_ahead: Number of steps

        Returns:
            List of predictions with confidence intervals
        """
        predictions = self.predict(metric_name, steps_ahead)

        # Simple confidence interval using historical std
        # In production, would use more sophisticated methods
        confidence_width = 0.1  # 10% confidence interval

        results = []
        for pred in predictions:
            results.append({
                "value": pred,
                "lower_bound": pred * (1 - confidence_width),
                "upper_bound": pred * (1 + confidence_width),
                "confidence_level": 0.95
            })

        return results

    def detect_trends(
        self,
        metric_name: str,
        historical_data: List[float],
        window_size: int = 10
    ) -> Dict[str, Any]:
        """
        Detect trends in data.

        Args:
            metric_name: Metric name
            historical_data: Historical values
            window_size: Window size for trend calculation

        Returns:
            Trend analysis
        """
        if len(historical_data) < window_size:
            return {
                "trend": "insufficient_data",
                "direction": "unknown"
            }

        # Calculate moving average
        moving_avg = []
        for i in range(len(historical_data) - window_size + 1):
            window = historical_data[i:i + window_size]
            moving_avg.append(np.mean(window))

        # Determine trend direction
        if len(moving_avg) < 2:
            return {
                "trend": "stable",
                "direction": "none",
                "slope": 0
            }

        # Calculate slope using linear regression
        X = np.arange(len(moving_avg)).reshape(-1, 1)
        y = np.array(moving_avg)

        # Simple slope calculation
        slope = (y[-1] - y[0]) / len(moving_avg)

        # Classify trend
        threshold = np.std(historical_data) * 0.1

        if abs(slope) < threshold:
            trend = "stable"
            direction = "none"
        elif slope > 0:
            trend = "increasing"
            direction = "up"
        else:
            trend = "decreasing"
            direction = "down"

        return {
            "trend": trend,
            "direction": direction,
            "slope": float(slope),
            "rate_of_change": float(slope / (np.mean(historical_data) + 1e-6)),
            "moving_average": moving_avg[-1]
        }

    def forecast_capacity(
        self,
        metric_name: str,
        current_value: float,
        growth_rate: float,
        threshold: float,
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """
        Forecast when capacity will be reached.

        Args:
            metric_name: Metric name
            current_value: Current value
            growth_rate: Daily growth rate
            threshold: Capacity threshold
            days_ahead: Days to forecast

        Returns:
            Capacity forecast
        """
        days_to_threshold = None
        projected_value = current_value

        for day in range(days_ahead):
            projected_value += projected_value * growth_rate

            if projected_value >= threshold and days_to_threshold is None:
                days_to_threshold = day

        return {
            "metric": metric_name,
            "current_value": current_value,
            "threshold": threshold,
            "days_to_threshold": days_to_threshold,
            "projected_value_at_30d": projected_value,
            "will_exceed_threshold": projected_value >= threshold,
            "forecast_date": (datetime.now() + timedelta(days=days_to_threshold)).isoformat() if days_to_threshold else None
        }
