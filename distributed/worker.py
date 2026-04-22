"""
Distributed test worker for executing tests on remote systems.
"""

import socket
import platform
from typing import Dict, Any, Optional
from datetime import datetime


class TestWorker:
    """
    Test worker that executes tests on a specific system.
    """

    def __init__(self, coordinator_url: Optional[str] = None):
        """
        Initialize test worker.

        Args:
            coordinator_url: URL of the coordinator
        """
        self.coordinator_url = coordinator_url
        self.worker_id = None
        self.status = "initializing"
        self.current_test = None
        self.system_info = self._collect_system_info()

    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect system information."""
        return {
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }

    def register(self) -> str:
        """
        Register with coordinator.

        Returns:
            Worker ID assigned by coordinator
        """
        # In production, this would make HTTP/RPC call to coordinator
        # For now, return mock ID
        self.worker_id = f"worker_{socket.gethostname()}"
        self.status = "idle"

        print(f"Worker registered: {self.worker_id}")
        print(f"System: {self.system_info['platform']} {self.system_info['platform_release']}")

        return self.worker_id

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get worker capabilities.

        Returns:
            Capabilities dictionary
        """
        return {
            "system_info": self.system_info,
            "supported_suites": [
                "rt-tests",
                "stress-ng",
                "iperf3",
                "fio",
                "stream",
                "unixbench"
            ],
            "max_concurrent_tests": 4,
            "available_resources": {
                "cpu_cores": 8,  # Would detect actual count
                "memory_gb": 16,  # Would detect actual amount
                "disk_gb": 100
            }
        }

    def execute_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single test case.

        Args:
            test_case: Test case specification

        Returns:
            Test result
        """
        self.status = "running"
        self.current_test = test_case["name"]

        try:
            start_time = datetime.now()

            # Execute test (simplified - in production would use executor)
            result = self._run_test(test_case)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            self.status = "idle"
            self.current_test = None

            return {
                "worker_id": self.worker_id,
                "test_name": test_case["name"],
                "status": "completed",
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration": duration,
                "result": result
            }

        except Exception as e:
            self.status = "error"

            return {
                "worker_id": self.worker_id,
                "test_name": test_case["name"],
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _run_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run test case (simplified implementation).

        Args:
            test_case: Test case to run

        Returns:
            Test result
        """
        # In production, this would use TestExecutor
        # For now, return mock result
        return {
            "metrics": {
                "latency": 45.2,
                "throughput": 950.0,
                "cpu_usage": 75.5
            },
            "output": "Test completed successfully",
            "exit_code": 0
        }

    def send_heartbeat(self) -> Dict[str, Any]:
        """
        Send heartbeat to coordinator.

        Returns:
            Heartbeat data
        """
        return {
            "worker_id": self.worker_id,
            "status": self.status,
            "current_test": self.current_test,
            "timestamp": datetime.now().isoformat(),
            "system_load": self._get_system_load()
        }

    def _get_system_load(self) -> Dict[str, Any]:
        """Get current system load metrics."""
        # In production, would collect actual metrics
        return {
            "cpu_percent": 25.0,
            "memory_percent": 50.0,
            "disk_usage_percent": 60.0
        }

    def get_status(self) -> Dict[str, Any]:
        """
        Get worker status.

        Returns:
            Current status
        """
        return {
            "worker_id": self.worker_id,
            "status": self.status,
            "current_test": self.current_test,
            "system_info": self.system_info,
            "capabilities": self.get_capabilities(),
            "system_load": self._get_system_load()
        }

    def shutdown(self):
        """Gracefully shutdown worker."""
        print(f"Shutting down worker {self.worker_id}")
        self.status = "shutdown"
