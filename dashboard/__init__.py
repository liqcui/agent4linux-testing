"""
Web dashboard for real-time test monitoring and visualization.
"""

from .app import create_app
from .server import DashboardServer

__all__ = ["create_app", "DashboardServer"]
