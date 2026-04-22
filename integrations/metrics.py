"""
Metrics collector and aggregator.
"""

from typing import Dict, List, Any, Optional
from collections import defaultdict
import statistics


class MetricsCollector:
    """
    Collects and aggregates metrics from multiple test runs.
    """

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = defaultdict(list)
        self.metadata = {}

    def add_metric(
        self,
        name: str,
        value: float,
        unit: str = "",
        category: str = "general",
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Add a metric.

        Args:
            name: Metric name
            value: Metric value
            unit: Unit of measurement
            category: Metric category
            tags: Optional tags for filtering
        """
        metric_data = {
            "value": value,
            "unit": unit,
            "category": category,
            "tags": tags or {}
        }

        self.metrics[name].append(metric_data)

    def get_metric(self, name: str) -> List[Dict[str, Any]]:
        """Get all values for a metric."""
        return self.metrics.get(name, [])

    def get_statistics(self, name: str) -> Optional[Dict[str, float]]:
        """
        Get statistical summary for a metric.

        Args:
            name: Metric name

        Returns:
            Dictionary with min, max, mean, median, stdev
        """
        values = [m["value"] for m in self.metrics.get(name, [])]

        if not values:
            return None

        stats = {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values)
        }

        if len(values) > 1:
            stats["stdev"] = statistics.stdev(values)
            stats["variance"] = statistics.variance(values)
        else:
            stats["stdev"] = 0
            stats["variance"] = 0

        # Calculate percentiles
        sorted_values = sorted(values)
        n = len(sorted_values)

        percentiles = [50, 90, 95, 99, 99.9]
        for p in percentiles:
            idx = int(n * p / 100)
            if idx >= n:
                idx = n - 1
            stats[f"p{p}"] = sorted_values[idx]

        return stats

    def get_all_metrics(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all collected metrics."""
        return dict(self.metrics)

    def get_categories(self) -> List[str]:
        """Get all metric categories."""
        categories = set()
        for metric_list in self.metrics.values():
            for metric in metric_list:
                categories.add(metric["category"])
        return sorted(categories)

    def filter_by_category(self, category: str) -> Dict[str, List[Dict[str, Any]]]:
        """Filter metrics by category."""
        filtered = {}

        for name, metric_list in self.metrics.items():
            category_metrics = [m for m in metric_list if m["category"] == category]
            if category_metrics:
                filtered[name] = category_metrics

        return filtered

    def filter_by_tags(self, tags: Dict[str, str]) -> Dict[str, List[Dict[str, Any]]]:
        """Filter metrics by tags."""
        filtered = {}

        for name, metric_list in self.metrics.items():
            matching_metrics = []
            for metric in metric_list:
                if all(metric["tags"].get(k) == v for k, v in tags.items()):
                    matching_metrics.append(metric)

            if matching_metrics:
                filtered[name] = matching_metrics

        return filtered

    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate comprehensive summary of all metrics.

        Returns:
            Summary dictionary
        """
        summary = {
            "total_metrics": len(self.metrics),
            "categories": self.get_categories(),
            "metrics": {}
        }

        for name in self.metrics.keys():
            stats = self.get_statistics(name)
            if stats:
                # Get unit from first metric
                unit = self.metrics[name][0]["unit"]
                category = self.metrics[name][0]["category"]

                summary["metrics"][name] = {
                    "statistics": stats,
                    "unit": unit,
                    "category": category
                }

        return summary

    def compare_with_baseline(
        self,
        baseline: 'MetricsCollector',
        threshold: float = 0.05
    ) -> Dict[str, Any]:
        """
        Compare metrics with baseline.

        Args:
            baseline: Baseline metrics collector
            threshold: Regression threshold (0.05 = 5%)

        Returns:
            Comparison results
        """
        comparison = {
            "regressions": [],
            "improvements": [],
            "stable": [],
            "new_metrics": [],
            "missing_metrics": []
        }

        baseline_metrics = set(baseline.metrics.keys())
        current_metrics = set(self.metrics.keys())

        # Find new and missing metrics
        comparison["new_metrics"] = list(current_metrics - baseline_metrics)
        comparison["missing_metrics"] = list(baseline_metrics - current_metrics)

        # Compare common metrics
        common_metrics = baseline_metrics & current_metrics

        for metric_name in common_metrics:
            baseline_stats = baseline.get_statistics(metric_name)
            current_stats = self.get_statistics(metric_name)

            if not baseline_stats or not current_stats:
                continue

            baseline_mean = baseline_stats["mean"]
            current_mean = current_stats["mean"]

            # Calculate change percentage
            if baseline_mean != 0:
                change_pct = (current_mean - baseline_mean) / baseline_mean
            else:
                change_pct = 0

            result = {
                "metric": metric_name,
                "baseline_mean": baseline_mean,
                "current_mean": current_mean,
                "change_percent": change_pct * 100,
                "unit": self.metrics[metric_name][0]["unit"]
            }

            # Determine if higher is better (depends on metric type)
            higher_is_better = self._is_higher_better(metric_name)

            if higher_is_better:
                if change_pct < -threshold:
                    comparison["regressions"].append(result)
                elif change_pct > threshold:
                    comparison["improvements"].append(result)
                else:
                    comparison["stable"].append(result)
            else:  # Lower is better (latency, errors, etc.)
                if change_pct > threshold:
                    comparison["regressions"].append(result)
                elif change_pct < -threshold:
                    comparison["improvements"].append(result)
                else:
                    comparison["stable"].append(result)

        return comparison

    def _is_higher_better(self, metric_name: str) -> bool:
        """
        Determine if higher values are better for a metric.

        Args:
            metric_name: Name of the metric

        Returns:
            True if higher is better
        """
        # Metrics where lower is better
        lower_is_better = [
            "latency", "delay", "error", "failure", "miss",
            "wait", "loss", "drop", "retry", "timeout"
        ]

        metric_lower = metric_name.lower()
        return not any(keyword in metric_lower for keyword in lower_is_better)

    def export_to_dict(self) -> Dict[str, Any]:
        """Export all data to dictionary."""
        return {
            "metrics": dict(self.metrics),
            "metadata": self.metadata,
            "summary": self.generate_summary()
        }

    def import_from_dict(self, data: Dict[str, Any]):
        """Import data from dictionary."""
        if "metrics" in data:
            self.metrics = defaultdict(list, data["metrics"])
        if "metadata" in data:
            self.metadata = data["metadata"]
