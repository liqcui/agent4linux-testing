"""
Test Executor - Executes test plans on Linux systems.
"""

import os
import subprocess
import json
from typing import Dict, List, Optional, Any
from datetime import datetime


class TestExecutor:
    """
    Executes test plans and collects results.

    Integrates with linux-testing suite and other testing tools.
    """

    def __init__(self, linux_testing_path: Optional[str] = None):
        """
        Initialize the executor.

        Args:
            linux_testing_path: Path to linux-testing repository
        """
        self.linux_testing_path = linux_testing_path or self._detect_linux_testing_path()
        self.results_dir = "./test_results"
        os.makedirs(self.results_dir, exist_ok=True)

    def _detect_linux_testing_path(self) -> Optional[str]:
        """
        Auto-detect linux-testing repository path.

        Returns:
            Path to repository or None
        """
        # Check common locations
        possible_paths = [
            "/Users/liqcui/goproject/github.com/liqcui/linux-testing",
            "../linux-testing",
            "../../linux-testing",
            os.path.expanduser("~/linux-testing")
        ]

        for path in possible_paths:
            if os.path.exists(path) and os.path.isdir(path):
                return os.path.abspath(path)

        return None

    def collect_system_info(self) -> Dict[str, Any]:
        """
        Collect system information.

        Returns:
            Dictionary with system specifications
        """
        info = {
            "timestamp": datetime.now().isoformat(),
            "hostname": subprocess.check_output(["hostname"]).decode().strip(),
            "kernel": subprocess.check_output(["uname", "-r"]).decode().strip(),
            "os": subprocess.check_output(["uname", "-s"]).decode().strip(),
            "architecture": subprocess.check_output(["uname", "-m"]).decode().strip(),
        }

        # CPU info
        try:
            with open("/proc/cpuinfo") as f:
                cpu_info = f.read()
                info["cpu_cores"] = cpu_info.count("processor")
                # Extract model name
                for line in cpu_info.split("\n"):
                    if "model name" in line:
                        info["cpu_model"] = line.split(":")[1].strip()
                        break
        except Exception:
            pass

        # Memory info
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if "MemTotal" in line:
                        info["memory_total"] = line.split()[1] + " " + line.split()[2]
                        break
        except Exception:
            pass

        return info

    def execute(
        self,
        test_plan: Dict[str, Any],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Execute test plan.

        Args:
            test_plan: Test plan to execute
            dry_run: If True, simulate without running tests

        Returns:
            Test results
        """
        results = {
            "test_plan_id": test_plan.get("id", "unknown"),
            "start_time": datetime.now().isoformat(),
            "test_cases": [],
            "summary": {}
        }

        if dry_run:
            print("🔍 DRY RUN MODE - Simulating test execution")

        for test_case in test_plan.get("test_cases", []):
            print(f"\n▶ Executing: {test_case['name']}")

            if dry_run:
                result = self._simulate_test_case(test_case)
            else:
                result = self._execute_test_case(test_case)

            results["test_cases"].append(result)

        results["end_time"] = datetime.now().isoformat()
        results["summary"] = self._generate_summary(results["test_cases"])

        return results

    def _execute_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single test case.

        Args:
            test_case: Test case specification

        Returns:
            Test result
        """
        result = {
            "name": test_case["name"],
            "suite": test_case["suite"],
            "start_time": datetime.now().isoformat(),
            "status": "unknown",
            "output": "",
            "metrics": {}
        }

        try:
            # Build command based on suite
            command = self._build_command(test_case)

            if command:
                print(f"  Running: {' '.join(command)}")
                # Execute command
                proc = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = proc.communicate()

                result["output"] = stdout
                result["error"] = stderr
                result["exit_code"] = proc.returncode
                result["status"] = "passed" if proc.returncode == 0 else "failed"

                # Parse metrics from output
                result["metrics"] = self._parse_metrics(
                    test_case["suite"],
                    stdout
                )
            else:
                result["status"] = "skipped"
                result["output"] = "Command builder not implemented for this suite"

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        result["end_time"] = datetime.now().isoformat()
        return result

    def _build_command(self, test_case: Dict[str, Any]) -> Optional[List[str]]:
        """
        Build command to execute test case.

        Args:
            test_case: Test case specification

        Returns:
            Command as list of strings
        """
        suite = test_case["suite"]
        params = test_case.get("parameters", {})

        if not self.linux_testing_path:
            return None

        # Map suite to script path
        suite_scripts = {
            "rt-tests": "tests/rt-tests/scripts/cyclictest_rt_full.sh",
            "stress-ng": "tests/stress-ng/scripts/test_memory.sh",
            "iperf3": "tests/iperf3/test_iperf3.sh",
            "fio": "tests/fio/run_fio_tests.sh",
            "stream": "tests/stream/run_stream.sh",
        }

        if suite in suite_scripts:
            script_path = os.path.join(self.linux_testing_path, suite_scripts[suite])
            if os.path.exists(script_path):
                cmd = ["sudo", "bash", script_path]
                # Add parameters
                for key, value in params.items():
                    cmd.extend([f"--{key}", str(value)])
                return cmd

        return None

    def _simulate_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate test case execution for dry run.

        Args:
            test_case: Test case specification

        Returns:
            Simulated result
        """
        import random

        return {
            "name": test_case["name"],
            "suite": test_case["suite"],
            "start_time": datetime.now().isoformat(),
            "end_time": datetime.now().isoformat(),
            "status": "simulated",
            "output": f"[DRY RUN] Would execute: {test_case['suite']}",
            "metrics": {
                "simulated_value": random.randint(100, 1000)
            }
        }

    def _parse_metrics(self, suite: str, output: str) -> Dict[str, Any]:
        """
        Parse metrics from test output.

        Args:
            suite: Test suite name
            output: Test output

        Returns:
            Dictionary of parsed metrics
        """
        metrics = {}

        # Suite-specific parsers
        if suite == "rt-tests":
            # Parse cyclictest output
            for line in output.split("\n"):
                if "Max Latencies:" in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        metrics["max_latency_us"] = int(parts[2])
                if "Avg Latencies:" in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        metrics["avg_latency_us"] = int(parts[2])

        elif suite == "stress-ng":
            # Parse stress-ng output
            for line in output.split("\n"):
                if "bogo ops/s" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "ops/s" and i > 0:
                            try:
                                metrics["bogo_ops_per_sec"] = float(parts[i-1])
                            except (ValueError, IndexError):
                                pass

        # Add more parsers for other suites

        return metrics

    def _generate_summary(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary of test results.

        Args:
            test_cases: List of test case results

        Returns:
            Summary dictionary
        """
        summary = {
            "total": len(test_cases),
            "passed": sum(1 for tc in test_cases if tc["status"] == "passed"),
            "failed": sum(1 for tc in test_cases if tc["status"] == "failed"),
            "error": sum(1 for tc in test_cases if tc["status"] == "error"),
            "skipped": sum(1 for tc in test_cases if tc["status"] == "skipped"),
        }

        summary["success_rate"] = (
            summary["passed"] / summary["total"] * 100
            if summary["total"] > 0 else 0
        )

        return summary
