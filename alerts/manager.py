"""
Alert manager for coordinating rules and notifications.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from .rules import RuleEngine, AlertRule
from .channels import BaseChannel


class AlertManager:
    """
    Manages alert rules, evaluates conditions, and sends notifications.
    """

    def __init__(self):
        """Initialize alert manager."""
        self.rule_engine = RuleEngine()
        self.channels = {}
        self.enabled = True

    def add_channel(self, name: str, channel: BaseChannel):
        """
        Register notification channel.

        Args:
            name: Channel name
            channel: Channel instance
        """
        self.channels[name] = channel
        print(f"Registered alert channel: {name}")

    def add_rule(self, rule: AlertRule):
        """
        Add alert rule.

        Args:
            rule: Alert rule
        """
        self.rule_engine.add_rule(rule)
        print(f"Added alert rule: {rule.name}")

    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove alert rule.

        Args:
            rule_name: Rule name

        Returns:
            True if removed
        """
        return self.rule_engine.remove_rule(rule_name)

    def evaluate(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate all rules and send alerts.

        Args:
            context: Context data for rule evaluation

        Returns:
            List of sent alerts
        """
        if not self.enabled:
            return []

        # Evaluate rules
        triggered_alerts = self.rule_engine.evaluate_all(context)

        # Send notifications
        sent_alerts = []
        for alert in triggered_alerts:
            if self._send_alert(alert):
                sent_alerts.append(alert)

        return sent_alerts

    def _send_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Send alert to configured channels.

        Args:
            alert: Alert data

        Returns:
            True if sent to at least one channel
        """
        channel_names = alert.get("channels", [])

        if not channel_names:
            # Send to all channels if none specified
            channel_names = list(self.channels.keys())

        sent_to_any = False

        for channel_name in channel_names:
            channel = self.channels.get(channel_name)

            if channel:
                try:
                    if channel.send(alert):
                        print(f"✓ Sent alert to {channel_name}: {alert['rule_name']}")
                        sent_to_any = True
                    else:
                        print(f"✗ Failed to send alert to {channel_name}")
                except Exception as e:
                    print(f"✗ Error sending to {channel_name}: {e}")

        return sent_to_any

    def test_alert(
        self,
        channel_name: str,
        test_message: str = "Test alert from Agent4Linux"
    ) -> bool:
        """
        Send test alert to a channel.

        Args:
            channel_name: Channel name
            test_message: Test message

        Returns:
            True if sent successfully
        """
        channel = self.channels.get(channel_name)

        if not channel:
            print(f"Channel not found: {channel_name}")
            return False

        test_alert = {
            "title": "Test Alert",
            "message": test_message,
            "severity": "info",
            "timestamp": datetime.now().isoformat(),
            "fields": {
                "Test": "This is a test alert",
                "Source": "Agent4Linux-Testing"
            }
        }

        return channel.send(test_alert)

    def enable(self):
        """Enable alert system."""
        self.enabled = True
        print("Alert system enabled")

    def disable(self):
        """Disable alert system."""
        self.enabled = False
        print("Alert system disabled")

    def get_status(self) -> Dict[str, Any]:
        """
        Get alert system status.

        Returns:
            Status information
        """
        return {
            "enabled": self.enabled,
            "rules_count": len(self.rule_engine.rules),
            "channels_count": len(self.channels),
            "channels": list(self.channels.keys()),
            "alert_history_count": len(self.rule_engine.alert_history)
        }

    def get_alert_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent alert history.

        Args:
            limit: Maximum alerts to return

        Returns:
            List of recent alerts
        """
        return self.rule_engine.get_alert_history(limit)

    def clear_history(self):
        """Clear alert history."""
        self.rule_engine.clear_history()
        print("Alert history cleared")

    def check_test_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check test results and trigger alerts.

        Args:
            results: Test results

        Returns:
            List of triggered alerts
        """
        context = {
            "max_latency": results.get("metrics", {}).get("max_latency", 0),
            "throughput": results.get("metrics", {}).get("throughput", 0),
            "failed_tests": results.get("failed_tests", 0),
            "verdict": results.get("verdict", ""),
            "score": results.get("score", 0),
            "regressions": results.get("regressions", []),
            "regression_count": len(results.get("regressions", [])),
            "is_anomaly": results.get("is_anomaly", False),
            "anomaly_score": results.get("anomaly_score", 0)
        }

        # Add all metrics to context
        context.update(results.get("metrics", {}))

        return self.evaluate(context)
