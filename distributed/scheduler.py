"""
Intelligent test scheduler for distributed execution.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import heapq


class TestScheduler:
    """
    Schedules tests across distributed workers based on priority and resources.
    """

    def __init__(self):
        """Initialize scheduler."""
        self.queue = []
        self.scheduled_tests = {}
        self.priority_levels = {
            "critical": 1,
            "high": 2,
            "medium": 3,
            "low": 4
        }

    def schedule_test(
        self,
        test_case: Dict[str, Any],
        priority: str = "medium",
        constraints: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Schedule a test for execution.

        Args:
            test_case: Test case to schedule
            priority: Test priority (critical, high, medium, low)
            constraints: Resource constraints and requirements

        Returns:
            Scheduled test ID
        """
        test_id = f"test_{len(self.scheduled_tests) + 1}"

        scheduled_test = {
            "id": test_id,
            "test_case": test_case,
            "priority": self.priority_levels.get(priority, 3),
            "constraints": constraints or {},
            "scheduled_at": datetime.now().isoformat(),
            "status": "queued"
        }

        # Add to priority queue
        heapq.heappush(
            self.queue,
            (scheduled_test["priority"], test_id, scheduled_test)
        )

        self.scheduled_tests[test_id] = scheduled_test

        return test_id

    def get_next_test(
        self,
        worker_capabilities: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get next test from queue matching worker capabilities.

        Args:
            worker_capabilities: Worker's capabilities

        Returns:
            Next test to execute or None
        """
        if not self.queue:
            return None

        # Get highest priority test
        while self.queue:
            _, test_id, test = heapq.heappop(self.queue)

            # Check if test matches worker capabilities
            if self._matches_capabilities(test, worker_capabilities):
                test["status"] = "assigned"
                return test

        return None

    def _matches_capabilities(
        self,
        test: Dict[str, Any],
        capabilities: Optional[Dict[str, Any]]
    ) -> bool:
        """Check if test requirements match worker capabilities."""
        if not capabilities:
            return True

        constraints = test.get("constraints", {})

        # Check suite support
        required_suite = test["test_case"].get("suite")
        if required_suite:
            supported = capabilities.get("supported_suites", [])
            if required_suite not in supported:
                return False

        # Check resource requirements
        required_resources = constraints.get("resources", {})
        available_resources = capabilities.get("available_resources", {})

        for resource, required in required_resources.items():
            available = available_resources.get(resource, 0)
            if available < required:
                return False

        return True

    def cancel_test(self, test_id: str) -> bool:
        """
        Cancel a scheduled test.

        Args:
            test_id: Test ID to cancel

        Returns:
            True if cancelled, False if not found
        """
        if test_id in self.scheduled_tests:
            self.scheduled_tests[test_id]["status"] = "cancelled"
            return True

        return False

    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get queue status.

        Returns:
            Queue statistics
        """
        queued = len([t for t in self.scheduled_tests.values() if t["status"] == "queued"])
        assigned = len([t for t in self.scheduled_tests.values() if t["status"] == "assigned"])
        completed = len([t for t in self.scheduled_tests.values() if t["status"] == "completed"])
        cancelled = len([t for t in self.scheduled_tests.values() if t["status"] == "cancelled"])

        return {
            "total_tests": len(self.scheduled_tests),
            "queued": queued,
            "assigned": assigned,
            "completed": completed,
            "cancelled": cancelled,
            "queue_length": len(self.queue)
        }

    def optimize_schedule(
        self,
        workers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Optimize test schedule based on available workers.

        Args:
            workers: List of available workers

        Returns:
            Optimization result
        """
        # Simple optimization: assign tests to workers with matching capabilities
        assignments = []

        for worker in workers:
            if worker["status"] == "idle":
                test = self.get_next_test(worker.get("capabilities"))

                if test:
                    assignments.append({
                        "worker_id": worker["id"],
                        "test_id": test["id"],
                        "test_name": test["test_case"]["name"]
                    })

        return {
            "assignments": assignments,
            "assigned_count": len(assignments),
            "remaining_queue": len(self.queue)
        }
