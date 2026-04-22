"""
Metrics visualization utilities.
"""

from typing import Dict, List, Any, Optional
import json
from pathlib import Path


class MetricsVisualizer:
    """
    Generates visualizations for test metrics.
    """

    def __init__(self, output_dir: str = "./visualizations"):
        """
        Initialize visualizer.

        Args:
            output_dir: Directory to save visualizations
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_metric_chart(
        self,
        metric_name: str,
        values: List[float],
        chart_type: str = "line",
        title: Optional[str] = None,
        unit: str = ""
    ) -> str:
        """
        Create a chart for a single metric.

        Args:
            metric_name: Name of the metric
            values: List of metric values
            chart_type: Type of chart (line, bar, histogram)
            title: Chart title
            unit: Unit of measurement

        Returns:
            Path to generated chart
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np

            fig, ax = plt.subplots(figsize=(10, 6))

            if chart_type == "line":
                ax.plot(values, marker='o', linewidth=2, markersize=6)
                ax.set_xlabel("Sample")
                ax.set_ylabel(f"{metric_name} ({unit})" if unit else metric_name)
                ax.grid(True, alpha=0.3)

            elif chart_type == "bar":
                ax.bar(range(len(values)), values, alpha=0.7)
                ax.set_xlabel("Sample")
                ax.set_ylabel(f"{metric_name} ({unit})" if unit else metric_name)
                ax.grid(True, alpha=0.3, axis='y')

            elif chart_type == "histogram":
                ax.hist(values, bins=20, alpha=0.7, edgecolor='black')
                ax.set_xlabel(f"{metric_name} ({unit})" if unit else metric_name)
                ax.set_ylabel("Frequency")
                ax.grid(True, alpha=0.3, axis='y')

            ax.set_title(title or f"{metric_name} Over Time")
            plt.tight_layout()

            output_path = self.output_dir / f"{metric_name.replace(' ', '_')}.png"
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            return str(output_path)

        except ImportError:
            return self._create_text_chart(metric_name, values, unit)

    def create_comparison_chart(
        self,
        baseline: Dict[str, float],
        current: Dict[str, float],
        title: str = "Baseline vs Current"
    ) -> str:
        """
        Create a comparison chart between baseline and current metrics.

        Args:
            baseline: Baseline metrics
            current: Current metrics
            title: Chart title

        Returns:
            Path to generated chart
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np

            metrics = sorted(set(baseline.keys()) & set(current.keys()))
            if not metrics:
                return ""

            x = np.arange(len(metrics))
            width = 0.35

            fig, ax = plt.subplots(figsize=(12, 6))

            baseline_values = [baseline[m] for m in metrics]
            current_values = [current[m] for m in metrics]

            ax.bar(x - width/2, baseline_values, width, label='Baseline', alpha=0.8)
            ax.bar(x + width/2, current_values, width, label='Current', alpha=0.8)

            ax.set_xlabel('Metrics')
            ax.set_ylabel('Value')
            ax.set_title(title)
            ax.set_xticks(x)
            ax.set_xticklabels(metrics, rotation=45, ha='right')
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')

            plt.tight_layout()

            output_path = self.output_dir / "comparison.png"
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            return str(output_path)

        except ImportError:
            return self._create_text_comparison(baseline, current)

    def create_percentile_chart(
        self,
        metric_name: str,
        percentiles: Dict[str, float],
        title: Optional[str] = None,
        unit: str = ""
    ) -> str:
        """
        Create a percentile distribution chart.

        Args:
            metric_name: Name of the metric
            percentiles: Dictionary of percentile values (p50, p90, p95, p99, etc.)
            title: Chart title
            unit: Unit of measurement

        Returns:
            Path to generated chart
        """
        try:
            import matplotlib.pyplot as plt

            # Extract percentile values
            percentile_keys = ['p50', 'p90', 'p95', 'p99']
            percentile_keys = [k for k in percentile_keys if k in percentiles]

            if not percentile_keys:
                return ""

            labels = [k.upper() for k in percentile_keys]
            values = [percentiles[k] for k in percentile_keys]

            fig, ax = plt.subplots(figsize=(8, 6))
            bars = ax.bar(labels, values, color=['green', 'yellow', 'orange', 'red'][:len(labels)], alpha=0.7)

            ax.set_ylabel(f"{metric_name} ({unit})" if unit else metric_name)
            ax.set_title(title or f"{metric_name} Percentile Distribution")
            ax.grid(True, alpha=0.3, axis='y')

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}',
                       ha='center', va='bottom')

            plt.tight_layout()

            output_path = self.output_dir / f"{metric_name.replace(' ', '_')}_percentiles.png"
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            return str(output_path)

        except ImportError:
            return self._create_text_percentiles(metric_name, percentiles, unit)

    def create_time_series(
        self,
        metrics: Dict[str, List[Dict[str, Any]]],
        title: str = "Metric Trends"
    ) -> str:
        """
        Create a time series chart for multiple metrics.

        Args:
            metrics: Dictionary of metric names to list of metric data
            title: Chart title

        Returns:
            Path to generated chart
        """
        try:
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(12, 6))

            for metric_name, metric_data in metrics.items():
                if not metric_data:
                    continue

                values = [m['value'] for m in metric_data]
                ax.plot(values, marker='o', label=metric_name, linewidth=2, markersize=4)

            ax.set_xlabel("Sample")
            ax.set_ylabel("Value")
            ax.set_title(title)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(True, alpha=0.3)

            plt.tight_layout()

            output_path = self.output_dir / "time_series.png"
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            return str(output_path)

        except ImportError:
            return self._create_text_time_series(metrics)

    def create_interactive_dashboard(
        self,
        metrics: Dict[str, Any],
        output_file: str = "dashboard.html"
    ) -> str:
        """
        Create an interactive HTML dashboard using plotly.

        Args:
            metrics: Metrics data
            output_file: Output HTML file name

        Returns:
            Path to generated dashboard
        """
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots

            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=("Metric Distribution", "Performance Trends",
                               "Percentile Analysis", "Category Breakdown")
            )

            # Add traces (placeholder implementation)
            # This would be customized based on actual metrics structure

            output_path = self.output_dir / output_file
            fig.write_html(str(output_path))

            return str(output_path)

        except ImportError:
            return self._create_static_dashboard(metrics, output_file)

    def create_regression_chart(
        self,
        regressions: List[Dict[str, Any]],
        improvements: List[Dict[str, Any]],
        stable: List[Dict[str, Any]]
    ) -> str:
        """
        Create a regression analysis visualization.

        Args:
            regressions: List of regressed metrics
            improvements: List of improved metrics
            stable: List of stable metrics

        Returns:
            Path to generated chart
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np

            categories = ['Regressions', 'Improvements', 'Stable']
            counts = [len(regressions), len(improvements), len(stable)]
            colors = ['red', 'green', 'gray']

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

            # Pie chart
            ax1.pie(counts, labels=categories, autopct='%1.1f%%',
                   colors=colors, startangle=90)
            ax1.set_title('Metric Status Distribution')

            # Bar chart with details
            all_metrics = regressions + improvements
            if all_metrics:
                metric_names = [m['metric'][:20] + '...' if len(m['metric']) > 20
                               else m['metric'] for m in all_metrics[:10]]
                changes = [m['change_percent'] for m in all_metrics[:10]]
                bar_colors = ['red' if c > 0 else 'green' for c in changes]

                ax2.barh(metric_names, changes, color=bar_colors, alpha=0.7)
                ax2.set_xlabel('Change (%)')
                ax2.set_title('Top Metric Changes')
                ax2.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
                ax2.grid(True, alpha=0.3, axis='x')

            plt.tight_layout()

            output_path = self.output_dir / "regression_analysis.png"
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            return str(output_path)

        except ImportError:
            return self._create_text_regression(regressions, improvements, stable)

    def _create_text_chart(self, metric_name: str, values: List[float], unit: str) -> str:
        """Fallback text-based chart when matplotlib is not available."""
        output_path = self.output_dir / f"{metric_name.replace(' ', '_')}.txt"

        max_val = max(values) if values else 1
        min_val = min(values) if values else 0
        range_val = max_val - min_val if max_val != min_val else 1

        with open(output_path, 'w') as f:
            f.write(f"{metric_name} ({unit})\n")
            f.write("=" * 60 + "\n\n")

            for i, val in enumerate(values):
                bar_length = int(((val - min_val) / range_val) * 40)
                bar = "#" * bar_length
                f.write(f"Sample {i:3d}: {bar} {val:.2f}\n")

            f.write(f"\nMin: {min_val:.2f}, Max: {max_val:.2f}\n")

        return str(output_path)

    def _create_text_comparison(self, baseline: Dict[str, float], current: Dict[str, float]) -> str:
        """Fallback text-based comparison."""
        output_path = self.output_dir / "comparison.txt"

        with open(output_path, 'w') as f:
            f.write("Baseline vs Current Comparison\n")
            f.write("=" * 60 + "\n\n")

            metrics = sorted(set(baseline.keys()) & set(current.keys()))
            for metric in metrics:
                b_val = baseline[metric]
                c_val = current[metric]
                change = ((c_val - b_val) / b_val * 100) if b_val != 0 else 0

                f.write(f"{metric}:\n")
                f.write(f"  Baseline: {b_val:.2f}\n")
                f.write(f"  Current:  {c_val:.2f}\n")
                f.write(f"  Change:   {change:+.2f}%\n\n")

        return str(output_path)

    def _create_text_percentiles(self, metric_name: str, percentiles: Dict[str, float], unit: str) -> str:
        """Fallback text-based percentiles."""
        output_path = self.output_dir / f"{metric_name.replace(' ', '_')}_percentiles.txt"

        with open(output_path, 'w') as f:
            f.write(f"{metric_name} Percentile Distribution ({unit})\n")
            f.write("=" * 60 + "\n\n")

            for key in ['p50', 'p90', 'p95', 'p99', 'p99.9']:
                if key in percentiles:
                    f.write(f"{key.upper():6s}: {percentiles[key]:.2f}\n")

        return str(output_path)

    def _create_text_time_series(self, metrics: Dict[str, List[Dict[str, Any]]]) -> str:
        """Fallback text-based time series."""
        output_path = self.output_dir / "time_series.txt"

        with open(output_path, 'w') as f:
            f.write("Metric Time Series\n")
            f.write("=" * 60 + "\n\n")

            for metric_name, metric_data in metrics.items():
                if not metric_data:
                    continue

                f.write(f"{metric_name}:\n")
                values = [m['value'] for m in metric_data]
                for i, val in enumerate(values):
                    f.write(f"  Sample {i:3d}: {val:.2f}\n")
                f.write("\n")

        return str(output_path)

    def _create_text_regression(
        self,
        regressions: List[Dict[str, Any]],
        improvements: List[Dict[str, Any]],
        stable: List[Dict[str, Any]]
    ) -> str:
        """Fallback text-based regression analysis."""
        output_path = self.output_dir / "regression_analysis.txt"

        with open(output_path, 'w') as f:
            f.write("Regression Analysis\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"Regressions: {len(regressions)}\n")
            for r in regressions[:5]:
                f.write(f"  - {r['metric']}: {r['change_percent']:+.2f}%\n")

            f.write(f"\nImprovements: {len(improvements)}\n")
            for i in improvements[:5]:
                f.write(f"  - {i['metric']}: {i['change_percent']:+.2f}%\n")

            f.write(f"\nStable: {len(stable)}\n")

        return str(output_path)

    def _create_static_dashboard(self, metrics: Dict[str, Any], output_file: str) -> str:
        """Fallback static HTML dashboard."""
        output_path = self.output_dir / output_file

        with open(output_path, 'w') as f:
            f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Metrics Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .metric { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
        .metric-name { font-weight: bold; font-size: 1.2em; }
        .metric-value { color: #007bff; font-size: 1.5em; }
    </style>
</head>
<body>
    <h1>Metrics Dashboard</h1>
""")

            # Add metrics
            for key, value in metrics.items():
                f.write(f"""
    <div class="metric">
        <div class="metric-name">{key}</div>
        <div class="metric-value">{value}</div>
    </div>
""")

            f.write("""
</body>
</html>
""")

        return str(output_path)
