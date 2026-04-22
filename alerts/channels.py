"""
Notification channels for alerts.
"""

import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from datetime import datetime


class BaseChannel:
    """Base class for notification channels."""

    def send(self, alert: Dict[str, Any]) -> bool:
        """
        Send alert notification.

        Args:
            alert: Alert data

        Returns:
            True if sent successfully
        """
        raise NotImplementedError


class SlackChannel(BaseChannel):
    """Slack notification channel."""

    def __init__(self, webhook_url: str):
        """
        Initialize Slack channel.

        Args:
            webhook_url: Slack webhook URL
        """
        self.webhook_url = webhook_url

    def send(self, alert: Dict[str, Any]) -> bool:
        """Send alert to Slack."""
        try:
            import requests

            # Format message
            message = self._format_message(alert)

            # Send to Slack
            response = requests.post(
                self.webhook_url,
                json={"text": message, "blocks": self._create_blocks(alert)},
                headers={"Content-Type": "application/json"}
            )

            return response.status_code == 200

        except Exception as e:
            print(f"Failed to send Slack alert: {e}")
            return False

    def _format_message(self, alert: Dict[str, Any]) -> str:
        """Format alert message for Slack."""
        severity = alert.get("severity", "info")
        emoji = {
            "critical": ":rotating_light:",
            "warning": ":warning:",
            "info": ":information_source:"
        }.get(severity, ":bell:")

        return f"{emoji} *{alert.get('title', 'Alert')}*\n{alert.get('message', '')}"

    def _create_blocks(self, alert: Dict[str, Any]) -> list:
        """Create Slack blocks for rich formatting."""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": alert.get("title", "Performance Alert")
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": alert.get("message", "")
                }
            }
        ]

        # Add fields if present
        if "fields" in alert:
            fields = []
            for key, value in alert["fields"].items():
                fields.append({
                    "type": "mrkdwn",
                    "text": f"*{key}:*\n{value}"
                })

            if fields:
                blocks.append({
                    "type": "section",
                    "fields": fields
                })

        return blocks


class PagerDutyChannel(BaseChannel):
    """PagerDuty notification channel."""

    def __init__(self, integration_key: str, api_url: str = "https://events.pagerduty.com/v2/enqueue"):
        """
        Initialize PagerDuty channel.

        Args:
            integration_key: PagerDuty integration key
            api_url: PagerDuty API URL
        """
        self.integration_key = integration_key
        self.api_url = api_url

    def send(self, alert: Dict[str, Any]) -> bool:
        """Send alert to PagerDuty."""
        try:
            import requests

            # Create event
            event = {
                "routing_key": self.integration_key,
                "event_action": "trigger",
                "payload": {
                    "summary": alert.get("title", "Performance Alert"),
                    "severity": self._map_severity(alert.get("severity", "info")),
                    "source": "agent4linux-testing",
                    "timestamp": datetime.now().isoformat(),
                    "custom_details": alert.get("fields", {})
                }
            }

            # Send to PagerDuty
            response = requests.post(
                self.api_url,
                json=event,
                headers={"Content-Type": "application/json"}
            )

            return response.status_code == 202

        except Exception as e:
            print(f"Failed to send PagerDuty alert: {e}")
            return False

    def _map_severity(self, severity: str) -> str:
        """Map alert severity to PagerDuty severity."""
        mapping = {
            "critical": "critical",
            "warning": "warning",
            "info": "info"
        }
        return mapping.get(severity, "info")


class EmailChannel(BaseChannel):
    """Email notification channel."""

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_addr: str,
        to_addrs: list
    ):
        """
        Initialize email channel.

        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port
            username: SMTP username
            password: SMTP password
            from_addr: From email address
            to_addrs: List of recipient addresses
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_addr = from_addr
        self.to_addrs = to_addrs

    def send(self, alert: Dict[str, Any]) -> bool:
        """Send alert via email."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = alert.get("title", "Performance Alert")
            msg['From'] = self.from_addr
            msg['To'] = ", ".join(self.to_addrs)

            # Create HTML body
            html_body = self._create_html_body(alert)
            msg.attach(MIMEText(html_body, 'html'))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            return True

        except Exception as e:
            print(f"Failed to send email alert: {e}")
            return False

    def _create_html_body(self, alert: Dict[str, Any]) -> str:
        """Create HTML email body."""
        severity = alert.get("severity", "info")
        color = {
            "critical": "#dc3545",
            "warning": "#ffc107",
            "info": "#17a2b8"
        }.get(severity, "#6c757d")

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .alert {{ padding: 20px; border-left: 4px solid {color}; }}
                .title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
                .message {{ margin-bottom: 15px; }}
                .fields {{ margin-top: 15px; }}
                .field {{ margin: 5px 0; }}
                .field-name {{ font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="alert">
                <div class="title">{alert.get('title', 'Performance Alert')}</div>
                <div class="message">{alert.get('message', '')}</div>
        """

        if "fields" in alert:
            html += '<div class="fields">'
            for key, value in alert["fields"].items():
                html += f'<div class="field"><span class="field-name">{key}:</span> {value}</div>'
            html += '</div>'

        html += """
            </div>
        </body>
        </html>
        """

        return html


class WebhookChannel(BaseChannel):
    """Generic webhook notification channel."""

    def __init__(self, webhook_url: str, headers: Optional[Dict[str, str]] = None):
        """
        Initialize webhook channel.

        Args:
            webhook_url: Webhook URL
            headers: Optional HTTP headers
        """
        self.webhook_url = webhook_url
        self.headers = headers or {"Content-Type": "application/json"}

    def send(self, alert: Dict[str, Any]) -> bool:
        """Send alert to webhook."""
        try:
            import requests

            response = requests.post(
                self.webhook_url,
                json=alert,
                headers=self.headers
            )

            return response.status_code in [200, 201, 202]

        except Exception as e:
            print(f"Failed to send webhook alert: {e}")
            return False
