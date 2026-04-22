"""
Dashboard server manager.
"""

import threading
from typing import Optional


class DashboardServer:
    """
    Manages the web dashboard server.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 5000, data_dir: str = "./test_results"):
        """
        Initialize dashboard server.

        Args:
            host: Host to bind to
            port: Port to listen on
            data_dir: Directory containing test results
        """
        self.host = host
        self.port = port
        self.data_dir = data_dir
        self.app = None
        self.server_thread = None
        self.running = False

    def start(self, debug: bool = False, background: bool = False):
        """
        Start the dashboard server.

        Args:
            debug: Enable debug mode
            background: Run in background thread
        """
        from .app import create_app

        self.app = create_app(self.data_dir)
        if not self.app:
            print("Failed to create Flask app")
            return

        if background:
            self.server_thread = threading.Thread(
                target=self._run_server,
                args=(debug,),
                daemon=True
            )
            self.server_thread.start()
            self.running = True
            print(f"Dashboard server started at http://{self.host}:{self.port}")
        else:
            self._run_server(debug)

    def _run_server(self, debug: bool = False):
        """Run the Flask server."""
        self.app.run(host=self.host, port=self.port, debug=debug, use_reloader=False)

    def stop(self):
        """Stop the dashboard server."""
        self.running = False
        print("Dashboard server stopped")

    def is_running(self) -> bool:
        """Check if server is running."""
        return self.running
