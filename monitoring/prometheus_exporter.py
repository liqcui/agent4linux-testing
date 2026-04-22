"""
Prometheus metrics exporter.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import threading


class PrometheusExporter:
    """
    Exports performance metrics in Prometheus format.
    """

    def __init__(self, port: int = 9090):
        """
        Initialize Prometheus exporter.

        Args:
            port: Port to expose metrics on
        """
        self.port = port
        self.metrics = {}
        self.server = None
        self.running = False

    def register_metric(
        self,
        name: str,
        metric_type: str = "gauge",
        help_text: str = "",
        labels: Optional[List[str]] = None
    ):
        """
        Register a metric.

        Args:
            name: Metric name
            metric_type: Type (gauge, counter, histogram, summary)
            help_text: Help text for metric
            labels: Label names
        """
        self.metrics[name] = {
            "type": metric_type,
            "help": help_text,
            "labels": labels or [],
            "values": {}
        }

    def set_metric(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """
        Set metric value.

        Args:
            name: Metric name
            value: Metric value
            labels: Label values
        """
        if name not in self.metrics:
            self.register_metric(name)

        label_key = self._label_key(labels or {})
        self.metrics[name]["values"][label_key] = value

    def inc_metric(
        self,
        name: str,
        amount: float = 1.0,
        labels: Optional[Dict[str, str]] = None
    ):
        """
        Increment counter metric.

        Args:
            name: Metric name
            amount: Amount to increment
            labels: Label values
        """
        if name not in self.metrics:
            self.register_metric(name, metric_type="counter")

        label_key = self._label_key(labels or {})
        current = self.metrics[name]["values"].get(label_key, 0)
        self.metrics[name]["values"][label_key] = current + amount

    def _label_key(self, labels: Dict[str, str]) -> str:
        """Create key from labels."""
        if not labels:
            return ""
        return ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))

    def export_metrics(self) -> str:
        """
        Export metrics in Prometheus format.

        Returns:
            Metrics in Prometheus exposition format
        """
        output = []

        for name, metric in self.metrics.items():
            # Add help text
            if metric["help"]:
                output.append(f"# HELP {name} {metric['help']}")

            # Add type
            output.append(f"# TYPE {name} {metric['type']}")

            # Add values
            for label_key, value in metric["values"].items():
                if label_key:
                    output.append(f"{name}{{{label_key}}} {value}")
                else:
                    output.append(f"{name} {value}")

        return "\n".join(output)

    def start_server(self):
        """Start HTTP server to expose metrics."""
        try:
            from http.server import HTTPServer, BaseHTTPRequestHandler

            exporter = self

            class MetricsHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == "/metrics":
                        metrics_text = exporter.export_metrics()
                        self.send_response(200)
                        self.send_header("Content-Type", "text/plain; version=0.0.4")
                        self.end_headers()
                        self.wfile.write(metrics_text.encode())
                    else:
                        self.send_response(404)
                        self.end_headers()

                def log_message(self, format, *args):
                    pass  # Suppress log messages

            self.server = HTTPServer(("0.0.0.0", self.port), MetricsHandler)
            self.running = True

            print(f"Prometheus exporter started on port {self.port}")
            print(f"Metrics available at http://localhost:{self.port}/metrics")

            # Run in separate thread
            server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            server_thread.start()

        except Exception as e:
            print(f"Failed to start Prometheus exporter: {e}")

    def stop_server(self):
        """Stop HTTP server."""
        if self.server:
            self.server.shutdown()
            self.running = False
            print("Prometheus exporter stopped")

    def record_test_metrics(self, results: Dict[str, Any]):
        """
        Record test results as Prometheus metrics.

        Args:
            results: Test results
        """
        # Record basic metrics
        self.set_metric(
            "agent4linux_test_score",
            results.get("score", 0),
            {"verdict": results.get("verdict", "unknown")}
        )

        self.set_metric(
            "agent4linux_test_duration_seconds",
            results.get("duration", 0)
        )

        # Record performance metrics
        metrics = results.get("metrics", {})

        for metric_name, value in metrics.items():
            if isinstance(value, (int, float)):
                prometheus_name = f"agent4linux_{metric_name.replace('-', '_')}"
                self.set_metric(prometheus_name, value)

        # Record test counts
        self.inc_metric(
            "agent4linux_tests_total",
            labels={"status": results.get("status", "unknown")}
        )

        if results.get("verdict") == "PASS":
            self.inc_metric("agent4linux_tests_passed_total")
        else:
            self.inc_metric("agent4linux_tests_failed_total")

    def get_sample_promql(self) -> List[str]:
        """
        Get sample PromQL queries.

        Returns:
            List of sample queries
        """
        return [
            "agent4linux_test_score",
            "rate(agent4linux_tests_total[5m])",
            "histogram_quantile(0.95, agent4linux_max_latency)",
            "agent4linux_tests_passed_total / agent4linux_tests_total",
            "rate(agent4linux_tests_failed_total[1h])"
        ]
