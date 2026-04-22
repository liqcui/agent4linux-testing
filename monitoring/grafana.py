"""
Grafana dashboard generator.
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class GrafanaDashboardGenerator:
    """
    Generates Grafana dashboards for performance metrics.
    """

    def __init__(self):
        """Initialize dashboard generator."""
        self.dashboard_template = self._create_base_template()

    def _create_base_template(self) -> Dict[str, Any]:
        """Create base dashboard template."""
        return {
            "dashboard": {
                "title": "Agent4Linux Performance Monitoring",
                "tags": ["performance", "linux", "testing"],
                "timezone": "browser",
                "schemaVersion": 16,
                "version": 1,
                "refresh": "30s",
                "panels": [],
                "templating": {
                    "list": []
                },
                "time": {
                    "from": "now-6h",
                    "to": "now"
                }
            },
            "overwrite": True
        }

    def generate_dashboard(
        self,
        metrics: Optional[List[str]] = None,
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate complete Grafana dashboard.

        Args:
            metrics: List of metric names to include
            output_file: Optional file to save dashboard JSON

        Returns:
            Dashboard JSON
        """
        dashboard = self._create_base_template()

        # Add default panels
        panels = [
            self._create_test_score_panel(),
            self._create_latency_panel(),
            self._create_throughput_panel(),
            self._create_test_rate_panel(),
            self._create_pass_rate_panel(),
            self._create_regressions_panel()
        ]

        # Position panels in grid
        for i, panel in enumerate(panels):
            row = (i // 2) * 8
            col = (i % 2) * 12

            panel["gridPos"] = {
                "h": 8,
                "w": 12,
                "x": col,
                "y": row
            }
            panel["id"] = i + 1

        dashboard["dashboard"]["panels"] = panels

        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(dashboard, f, indent=2)

        return dashboard

    def _create_test_score_panel(self) -> Dict[str, Any]:
        """Create test score panel."""
        return {
            "title": "Test Score",
            "type": "stat",
            "targets": [{
                "expr": "agent4linux_test_score",
                "legendFormat": "Score"
            }],
            "options": {
                "graphMode": "area",
                "colorMode": "value",
                "orientation": "auto",
                "textMode": "value_and_name",
                "reduceOptions": {
                    "values": False,
                    "calcs": ["lastNotNull"]
                }
            },
            "fieldConfig": {
                "defaults": {
                    "min": 0,
                    "max": 100,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"value": 0, "color": "red"},
                            {"value": 70, "color": "yellow"},
                            {"value": 90, "color": "green"}
                        ]
                    }
                }
            }
        }

    def _create_latency_panel(self) -> Dict[str, Any]:
        """Create latency time series panel."""
        return {
            "title": "Latency Over Time",
            "type": "graph",
            "targets": [{
                "expr": "agent4linux_max_latency",
                "legendFormat": "Max Latency (μs)"
            }],
            "yaxes": [{
                "format": "µs",
                "label": "Latency"
            }],
            "xaxis": {
                "mode": "time"
            },
            "lines": True,
            "fill": 1,
            "linewidth": 2,
            "points": False,
            "pointradius": 2,
            "bars": False,
            "stack": False,
            "percentage": False,
            "legend": {
                "show": True,
                "values": True,
                "min": True,
                "max": True,
                "current": True,
                "total": False,
                "avg": True
            },
            "nullPointMode": "connected",
            "tooltip": {
                "shared": True,
                "sort": 0,
                "value_type": "individual"
            }
        }

    def _create_throughput_panel(self) -> Dict[str, Any]:
        """Create throughput panel."""
        return {
            "title": "Throughput",
            "type": "graph",
            "targets": [{
                "expr": "agent4linux_throughput",
                "legendFormat": "Throughput (Mbps)"
            }],
            "yaxes": [{
                "format": "Mbits",
                "label": "Throughput"
            }],
            "xaxis": {
                "mode": "time"
            },
            "lines": True,
            "fill": 1,
            "linewidth": 2
        }

    def _create_test_rate_panel(self) -> Dict[str, Any]:
        """Create test execution rate panel."""
        return {
            "title": "Test Execution Rate",
            "type": "graph",
            "targets": [{
                "expr": "rate(agent4linux_tests_total[5m])",
                "legendFormat": "Tests/sec"
            }],
            "yaxes": [{
                "format": "ops",
                "label": "Rate"
            }],
            "xaxis": {
                "mode": "time"
            },
            "lines": True,
            "fill": 1
        }

    def _create_pass_rate_panel(self) -> Dict[str, Any]:
        """Create test pass rate panel."""
        return {
            "title": "Test Pass Rate",
            "type": "stat",
            "targets": [{
                "expr": "agent4linux_tests_passed_total / agent4linux_tests_total * 100",
                "legendFormat": "Pass Rate"
            }],
            "options": {
                "graphMode": "area",
                "colorMode": "value",
                "textMode": "value"
            },
            "fieldConfig": {
                "defaults": {
                    "unit": "percent",
                    "min": 0,
                    "max": 100,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"value": 0, "color": "red"},
                            {"value": 80, "color": "yellow"},
                            {"value": 95, "color": "green"}
                        ]
                    }
                }
            }
        }

    def _create_regressions_panel(self) -> Dict[str, Any]:
        """Create regressions counter panel."""
        return {
            "title": "Performance Regressions (24h)",
            "type": "stat",
            "targets": [{
                "expr": "increase(agent4linux_regressions_total[24h])",
                "legendFormat": "Regressions"
            }],
            "options": {
                "colorMode": "background",
                "graphMode": "none",
                "textMode": "value"
            },
            "fieldConfig": {
                "defaults": {
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"value": 0, "color": "green"},
                            {"value": 1, "color": "yellow"},
                            {"value": 5, "color": "red"}
                        ]
                    }
                }
            }
        }

    def generate_alert_rules(self, output_file: str = "grafana_alerts.json") -> Dict[str, Any]:
        """
        Generate Grafana alert rules.

        Args:
            output_file: Output file path

        Returns:
            Alert rules JSON
        """
        alerts = {
            "groups": [{
                "name": "performance_alerts",
                "interval": "1m",
                "rules": [
                    {
                        "alert": "HighLatency",
                        "expr": "agent4linux_max_latency > 100",
                        "for": "5m",
                        "labels": {
                            "severity": "warning"
                        },
                        "annotations": {
                            "summary": "High latency detected",
                            "description": "Latency is above 100μs for 5 minutes"
                        }
                    },
                    {
                        "alert": "LowPassRate",
                        "expr": "agent4linux_tests_passed_total / agent4linux_tests_total < 0.95",
                        "for": "10m",
                        "labels": {
                            "severity": "warning"
                        },
                        "annotations": {
                            "summary": "Low test pass rate",
                            "description": "Pass rate is below 95%"
                        }
                    },
                    {
                        "alert": "PerformanceRegression",
                        "expr": "increase(agent4linux_regressions_total[1h]) > 0",
                        "for": "1m",
                        "labels": {
                            "severity": "critical"
                        },
                        "annotations": {
                            "summary": "Performance regression detected",
                            "description": "One or more metrics have regressed"
                        }
                    }
                ]
            }]
        }

        with open(output_file, 'w') as f:
            json.dump(alerts, f, indent=2)

        return alerts

    def export_to_file(self, dashboard: Dict[str, Any], filename: str):
        """
        Export dashboard to file.

        Args:
            dashboard: Dashboard JSON
            filename: Output filename
        """
        with open(filename, 'w') as f:
            json.dump(dashboard, f, indent=2)

        print(f"Dashboard exported to {filename}")
