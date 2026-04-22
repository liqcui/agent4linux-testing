"""
Historical tracking manager.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import statistics

from .database import HistoryDatabase


class HistoryTracker:
    """
    Tracks and analyzes historical test data.
    """

    def __init__(self, db_path: str = "./history.db"):
        """
        Initialize history tracker.

        Args:
            db_path: Path to database file
        """
        self.db = HistoryDatabase(db_path)

    def record_test_run(self, test_data: Dict[str, Any]) -> int:
        """
        Record a test run.

        Args:
            test_data: Test run data

        Returns:
            Run ID
        """
        return self.db.save_test_run(test_data)

    def get_recent_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent test runs.

        Args:
            limit: Number of runs to return

        Returns:
            List of test runs
        """
        return self.db.get_test_runs(limit=limit)

    def get_metric_trend(self, metric_name: str, days: int = 7) -> Dict[str, Any]:
        """
        Get trend for a metric.

        Args:
            metric_name: Metric name
            days: Number of days

        Returns:
            Trend analysis
        """
        history = self.db.get_metric_history(metric_name, limit=1000)

        # Filter by date range
        cutoff = datetime.now() - timedelta(days=days)
        recent = [h for h in history
                 if datetime.fromisoformat(h['timestamp']) >= cutoff]

        if not recent:
            return {
                'metric': metric_name,
                'trend': 'no_data',
                'data_points': 0
            }

        values = [h['value'] for h in recent]

        # Calculate trend
        if len(values) < 2:
            trend_direction = 'stable'
        else:
            first_half_avg = statistics.mean(values[:len(values)//2])
            second_half_avg = statistics.mean(values[len(values)//2:])

            change_pct = ((second_half_avg - first_half_avg) / first_half_avg * 100
                         if first_half_avg != 0 else 0)

            if abs(change_pct) < 5:
                trend_direction = 'stable'
            elif change_pct > 0:
                trend_direction = 'increasing'
            else:
                trend_direction = 'decreasing'

        return {
            'metric': metric_name,
            'trend': trend_direction,
            'change_percent': change_pct if len(values) >= 2 else 0,
            'current_avg': statistics.mean(values) if values else 0,
            'min': min(values) if values else 0,
            'max': max(values) if values else 0,
            'data_points': len(recent),
            'history': recent
        }

    def compare_with_baseline(self, test_id: str, baseline_name: str) -> Dict[str, Any]:
        """
        Compare a test run with a baseline.

        Args:
            test_id: Test run ID
            baseline_name: Baseline name

        Returns:
            Comparison results
        """
        baseline = self.db.get_baseline(baseline_name)
        if not baseline:
            return {'error': f'Baseline {baseline_name} not found'}

        # Get current test run
        current_runs = self.db.get_test_runs(limit=1000)
        current = next((r for r in current_runs if r['test_id'] == test_id), None)

        if not current:
            return {'error': f'Test run {test_id} not found'}

        # Get metrics for both
        baseline_metrics = self.db.get_metrics_for_run(baseline['run_id'])
        current_metrics = self.db.get_metrics_for_run(current['id'])

        # Convert to dict for easier comparison
        baseline_dict = {m['name']: m['value'] for m in baseline_metrics}
        current_dict = {m['name']: m['value'] for m in current_metrics}

        # Compare
        comparison = {
            'baseline': baseline_name,
            'baseline_score': baseline['score'],
            'current_score': current['score'],
            'regressions': [],
            'improvements': [],
            'stable': []
        }

        for metric_name in set(baseline_dict.keys()) & set(current_dict.keys()):
            baseline_val = baseline_dict[metric_name]
            current_val = current_dict[metric_name]

            if baseline_val == 0:
                continue

            change_pct = ((current_val - baseline_val) / baseline_val) * 100

            result = {
                'metric': metric_name,
                'baseline': baseline_val,
                'current': current_val,
                'change_percent': change_pct
            }

            # Determine if higher is better
            lower_is_better = any(kw in metric_name.lower()
                                 for kw in ['latency', 'error', 'delay'])

            if lower_is_better:
                if change_pct > 5:
                    comparison['regressions'].append(result)
                elif change_pct < -5:
                    comparison['improvements'].append(result)
                else:
                    comparison['stable'].append(result)
            else:
                if change_pct < -5:
                    comparison['regressions'].append(result)
                elif change_pct > 5:
                    comparison['improvements'].append(result)
                else:
                    comparison['stable'].append(result)

        return comparison

    def create_baseline_from_run(self, test_id: str, baseline_name: str,
                                  description: str = "") -> int:
        """
        Create a baseline from a test run.

        Args:
            test_id: Test ID
            baseline_name: Name for the baseline
            description: Description

        Returns:
            Baseline ID
        """
        # Find the run
        runs = self.db.get_test_runs(limit=1000)
        run = next((r for r in runs if r['test_id'] == test_id), None)

        if not run:
            raise ValueError(f"Test run {test_id} not found")

        return self.db.create_baseline(baseline_name, run['id'], description)

    def get_performance_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Get performance summary for the last N days.

        Args:
            days: Number of days

        Returns:
            Performance summary
        """
        runs = self.db.get_test_runs(limit=1000)

        # Filter by date
        cutoff = datetime.now() - timedelta(days=days)
        recent = [r for r in runs
                 if datetime.fromisoformat(r['timestamp']) >= cutoff]

        if not recent:
            return {
                'period_days': days,
                'total_runs': 0
            }

        # Calculate stats
        pass_count = sum(1 for r in recent if r['verdict'] == 'PASS')
        scores = [r['score'] for r in recent if r['score'] > 0]

        return {
            'period_days': days,
            'total_runs': len(recent),
            'pass_count': pass_count,
            'fail_count': len(recent) - pass_count,
            'pass_rate': (pass_count / len(recent) * 100) if recent else 0,
            'avg_score': statistics.mean(scores) if scores else 0,
            'min_score': min(scores) if scores else 0,
            'max_score': max(scores) if scores else 0,
            'recent_runs': recent[:10]
        }

    def detect_anomalies(self, metric_name: str, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """
        Detect anomalies in metric values using standard deviation.

        Args:
            metric_name: Metric name
            threshold: Standard deviation threshold

        Returns:
            List of anomalies
        """
        history = self.db.get_metric_history(metric_name, limit=1000)

        if len(history) < 10:
            return []

        values = [h['value'] for h in history]
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)

        anomalies = []
        for h in history:
            z_score = abs((h['value'] - mean) / stdev) if stdev > 0 else 0
            if z_score > threshold:
                anomalies.append({
                    'timestamp': h['timestamp'],
                    'value': h['value'],
                    'z_score': z_score,
                    'deviation_from_mean': h['value'] - mean
                })

        return anomalies

    def export_to_json(self, output_file: str, days: int = 30):
        """
        Export historical data to JSON.

        Args:
            output_file: Output file path
            days: Number of days to export
        """
        import json

        runs = self.db.get_test_runs(limit=1000)
        cutoff = datetime.now() - timedelta(days=days)
        recent = [r for r in runs
                 if datetime.fromisoformat(r['timestamp']) >= cutoff]

        # Get metrics for each run
        for run in recent:
            run['metrics'] = self.db.get_metrics_for_run(run['id'])

        data = {
            'export_date': datetime.now().isoformat(),
            'period_days': days,
            'total_runs': len(recent),
            'runs': recent
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

    def close(self):
        """Close database connection."""
        self.db.close()
