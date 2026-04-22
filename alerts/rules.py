"""
Alert rules and rule engine.
"""

from typing import Dict, List, Any, Optional, Callable
from datetime import datetime


class AlertRule:
    """
    Defines an alert rule with conditions and actions.
    """

    def __init__(
        self,
        name: str,
        condition: Callable[[Dict[str, Any]], bool],
        severity: str = "warning",
        message_template: str = "",
        channels: Optional[List[str]] = None,
        cooldown_seconds: int = 300
    ):
        """
        Initialize alert rule.

        Args:
            name: Rule name
            condition: Function that evaluates condition
            severity: Alert severity (critical, warning, info)
            message_template: Message template with {placeholders}
            channels: List of channel names to send to
            cooldown_seconds: Cooldown period between alerts
        """
        self.name = name
        self.condition = condition
        self.severity = severity
        self.message_template = message_template
        self.channels = channels or []
        self.cooldown_seconds = cooldown_seconds
        self.last_triggered = None

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate rule condition.

        Args:
            context: Context data

        Returns:
            True if condition met
        """
        return self.condition(context)

    def is_in_cooldown(self) -> bool:
        """Check if rule is in cooldown period."""
        if not self.last_triggered:
            return False

        elapsed = (datetime.now() - self.last_triggered).total_seconds()
        return elapsed < self.cooldown_seconds

    def mark_triggered(self):
        """Mark rule as triggered."""
        self.last_triggered = datetime.now()

    def format_message(self, context: Dict[str, Any]) -> str:
        """
        Format alert message.

        Args:
            context: Context data

        Returns:
            Formatted message
        """
        try:
            return self.message_template.format(**context)
        except KeyError:
            return self.message_template


class RuleEngine:
    """
    Evaluates alert rules and triggers notifications.
    """

    def __init__(self):
        """Initialize rule engine."""
        self.rules = []
        self.alert_history = []

    def add_rule(self, rule: AlertRule):
        """
        Add alert rule.

        Args:
            rule: Alert rule to add
        """
        self.rules.append(rule)

    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove alert rule by name.

        Args:
            rule_name: Name of rule to remove

        Returns:
            True if removed
        """
        initial_len = len(self.rules)
        self.rules = [r for r in self.rules if r.name != rule_name]
        return len(self.rules) < initial_len

    def evaluate_all(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate all rules.

        Args:
            context: Context data

        Returns:
            List of triggered alerts
        """
        triggered_alerts = []

        for rule in self.rules:
            # Skip if in cooldown
            if rule.is_in_cooldown():
                continue

            # Evaluate condition
            if rule.evaluate(context):
                alert = {
                    "rule_name": rule.name,
                    "severity": rule.severity,
                    "title": f"Alert: {rule.name}",
                    "message": rule.format_message(context),
                    "channels": rule.channels,
                    "timestamp": datetime.now().isoformat(),
                    "fields": context
                }

                triggered_alerts.append(alert)
                rule.mark_triggered()

                # Record in history
                self.alert_history.append(alert)

        return triggered_alerts

    def get_rule(self, rule_name: str) -> Optional[AlertRule]:
        """Get rule by name."""
        return next((r for r in self.rules if r.name == rule_name), None)

    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent alert history."""
        return self.alert_history[-limit:]

    def clear_history(self):
        """Clear alert history."""
        self.alert_history.clear()


# Predefined rule factories
def create_latency_rule(
    threshold: float,
    severity: str = "warning",
    channels: Optional[List[str]] = None
) -> AlertRule:
    """
    Create latency threshold rule.

    Args:
        threshold: Latency threshold in microseconds
        severity: Alert severity
        channels: Notification channels

    Returns:
        Alert rule
    """
    def condition(context: Dict[str, Any]) -> bool:
        latency = context.get("max_latency", 0)
        return latency > threshold

    return AlertRule(
        name=f"latency_above_{threshold}us",
        condition=condition,
        severity=severity,
        message_template=f"Latency {{max_latency}}μs exceeds threshold {threshold}μs",
        channels=channels
    )


def create_regression_rule(
    threshold_percent: float = 5.0,
    severity: str = "warning",
    channels: Optional[List[str]] = None
) -> AlertRule:
    """
    Create regression detection rule.

    Args:
        threshold_percent: Regression threshold percentage
        severity: Alert severity
        channels: Notification channels

    Returns:
        Alert rule
    """
    def condition(context: Dict[str, Any]) -> bool:
        regressions = context.get("regressions", [])
        return len(regressions) > 0

    return AlertRule(
        name="performance_regression",
        condition=condition,
        severity=severity,
        message_template="Performance regression detected: {regression_count} metrics degraded",
        channels=channels
    )


def create_anomaly_rule(
    severity: str = "warning",
    channels: Optional[List[str]] = None
) -> AlertRule:
    """
    Create anomaly detection rule.

    Args:
        severity: Alert severity
        channels: Notification channels

    Returns:
        Alert rule
    """
    def condition(context: Dict[str, Any]) -> bool:
        return context.get("is_anomaly", False)

    return AlertRule(
        name="anomaly_detected",
        condition=condition,
        severity=severity,
        message_template="Anomaly detected in {metric}: value={value}, score={anomaly_score}",
        channels=channels
    )


def create_failure_rule(
    failure_threshold: int = 1,
    severity: str = "critical",
    channels: Optional[List[str]] = None
) -> AlertRule:
    """
    Create test failure rule.

    Args:
        failure_threshold: Number of failures to trigger alert
        severity: Alert severity
        channels: Notification channels

    Returns:
        Alert rule
    """
    def condition(context: Dict[str, Any]) -> bool:
        failed = context.get("failed_tests", 0)
        return failed >= failure_threshold

    return AlertRule(
        name="test_failures",
        condition=condition,
        severity=severity,
        message_template="Test failures detected: {failed_tests} tests failed",
        channels=channels
    )
