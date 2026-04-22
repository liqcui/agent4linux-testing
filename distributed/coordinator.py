"""
Distributed test coordinator for multi-system testing.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class DistributedCoordinator:
    """
    Coordinates distributed test execution across multiple systems.

    Manages test distribution, worker orchestration, and result aggregation.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize distributed coordinator.

        Args:
            config_path: Path to configuration file
        """
        self.workers = []
        self.active_tests = {}
        self.results = {}
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load coordinator configuration."""
        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                return json.load(f)

        # Default configuration
        return {
            "max_workers": 10,
            "timeout": 3600,
            "retry_attempts": 3,
            "health_check_interval": 30,
            "result_aggregation": "merge"
        }

    def register_worker(self, worker_info: Dict[str, Any]) -> str:
        """
        Register a test worker.

        Args:
            worker_info: Worker information (hostname, capabilities, etc.)

        Returns:
            Worker ID
        """
        worker_id = f"worker_{len(self.workers) + 1}"

        worker = {
            "id": worker_id,
            "info": worker_info,
            "status": "idle",
            "registered_at": datetime.now().isoformat(),
            "last_heartbeat": datetime.now().isoformat(),
            "current_task": None
        }

        self.workers.append(worker)
        print(f"✓ Registered worker: {worker_id} ({worker_info.get('hostname', 'unknown')})")

        return worker_id

    def get_available_workers(self) -> List[Dict[str, Any]]:
        """
        Get list of available workers.

        Returns:
            List of idle workers
        """
        return [w for w in self.workers if w["status"] == "idle"]

    def distribute_test_plan(self, test_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Distribute test plan across available workers.

        Args:
            test_plan: Test plan to distribute

        Returns:
            Distribution plan with worker assignments
        """
        test_cases = test_plan.get("test_cases", [])
        available_workers = self.get_available_workers()

        if not available_workers:
            return {
                "status": "no_workers",
                "message": "No available workers for test execution"
            }

        # Distribute tests across workers
        distribution = {
            "plan_id": test_plan.get("id", f"plan_{datetime.now().timestamp()}"),
            "total_tests": len(test_cases),
            "worker_count": len(available_workers),
            "assignments": []
        }

        # Round-robin distribution
        for i, test_case in enumerate(test_cases):
            worker = available_workers[i % len(available_workers)]

            assignment = {
                "worker_id": worker["id"],
                "test_case": test_case,
                "assigned_at": datetime.now().isoformat()
            }

            distribution["assignments"].append(assignment)

            # Update worker status
            worker["status"] = "assigned"
            worker["current_task"] = test_case["name"]

        return distribution

    async def execute_distributed_test(
        self,
        test_plan: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute test plan in distributed manner.

        Args:
            test_plan: Test plan to execute
            timeout: Execution timeout in seconds

        Returns:
            Aggregated test results
        """
        timeout = timeout or self.config["timeout"]

        # Distribute tests
        distribution = self.distribute_test_plan(test_plan)

        if distribution.get("status") == "no_workers":
            return distribution

        # Create execution tasks
        tasks = []
        for assignment in distribution["assignments"]:
            task = asyncio.create_task(
                self._execute_on_worker(assignment)
            )
            tasks.append(task)

        # Wait for all tasks with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=timeout
            )

            # Aggregate results
            return self._aggregate_results(distribution, results)

        except asyncio.TimeoutError:
            return {
                "status": "timeout",
                "message": f"Execution exceeded timeout of {timeout}s",
                "partial_results": self.results
            }

    async def _execute_on_worker(self, assignment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute test on assigned worker.

        Args:
            assignment: Test assignment

        Returns:
            Test result
        """
        worker_id = assignment["worker_id"]
        test_case = assignment["test_case"]

        worker = next(w for w in self.workers if w["id"] == worker_id)

        try:
            # Update worker status
            worker["status"] = "running"

            # Simulate test execution (in real implementation, this would be an RPC call)
            result = await self._mock_test_execution(worker, test_case)

            # Update worker status
            worker["status"] = "idle"
            worker["current_task"] = None

            return result

        except Exception as e:
            worker["status"] = "error"
            return {
                "worker_id": worker_id,
                "test_case": test_case["name"],
                "status": "error",
                "error": str(e)
            }

    async def _mock_test_execution(
        self,
        worker: Dict[str, Any],
        test_case: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mock test execution (replace with actual RPC in production)."""
        await asyncio.sleep(0.1)  # Simulate work

        return {
            "worker_id": worker["id"],
            "test_case": test_case["name"],
            "status": "completed",
            "start_time": datetime.now().isoformat(),
            "end_time": datetime.now().isoformat(),
            "metrics": {
                "duration": 0.1,
                "success": True
            }
        }

    def _aggregate_results(
        self,
        distribution: Dict[str, Any],
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aggregate results from multiple workers.

        Args:
            distribution: Distribution plan
            results: List of worker results

        Returns:
            Aggregated results
        """
        aggregated = {
            "plan_id": distribution["plan_id"],
            "total_tests": distribution["total_tests"],
            "completed_tests": len([r for r in results if isinstance(r, dict) and r.get("status") == "completed"]),
            "failed_tests": len([r for r in results if isinstance(r, dict) and r.get("status") == "error"]),
            "worker_results": results,
            "aggregation_time": datetime.now().isoformat()
        }

        # Calculate overall statistics
        completed = [r for r in results if isinstance(r, dict) and r.get("status") == "completed"]

        if completed:
            total_duration = sum(r.get("metrics", {}).get("duration", 0) for r in completed)
            aggregated["total_duration"] = total_duration
            aggregated["avg_duration"] = total_duration / len(completed)

        return aggregated

    def get_worker_status(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific worker.

        Args:
            worker_id: Worker ID

        Returns:
            Worker status or None
        """
        worker = next((w for w in self.workers if w["id"] == worker_id), None)
        return worker

    def get_cluster_status(self) -> Dict[str, Any]:
        """
        Get overall cluster status.

        Returns:
            Cluster status information
        """
        idle_count = len([w for w in self.workers if w["status"] == "idle"])
        running_count = len([w for w in self.workers if w["status"] == "running"])
        error_count = len([w for w in self.workers if w["status"] == "error"])

        return {
            "total_workers": len(self.workers),
            "idle_workers": idle_count,
            "running_workers": running_count,
            "error_workers": error_count,
            "active_tests": len(self.active_tests),
            "timestamp": datetime.now().isoformat()
        }

    def scale_workers(self, target_count: int) -> Dict[str, Any]:
        """
        Scale worker pool to target count.

        Args:
            target_count: Desired number of workers

        Returns:
            Scaling operation result
        """
        current_count = len(self.workers)

        if target_count > current_count:
            # Scale up
            to_add = target_count - current_count
            return {
                "action": "scale_up",
                "workers_to_add": to_add,
                "message": f"Add {to_add} workers to reach {target_count}"
            }
        elif target_count < current_count:
            # Scale down
            to_remove = current_count - target_count
            idle_workers = self.get_available_workers()

            if len(idle_workers) < to_remove:
                return {
                    "action": "scale_down",
                    "status": "partial",
                    "message": f"Can only remove {len(idle_workers)} idle workers"
                }

            # Remove idle workers
            for i in range(to_remove):
                self.workers.remove(idle_workers[i])

            return {
                "action": "scale_down",
                "workers_removed": to_remove,
                "new_count": len(self.workers)
            }
        else:
            return {
                "action": "no_change",
                "message": "Already at target worker count"
            }
