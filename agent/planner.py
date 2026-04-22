"""
Test Planner - Designs test cases based on requirements using AI.
"""

from typing import Dict, List, Optional, Any
from models.prompts import TEST_DESIGN_PROMPT


class TestPlanner:
    """
    AI-powered test case designer.

    Uses LLM to understand requirements and generate comprehensive test plans.
    """

    def __init__(self, llm_client):
        """
        Initialize the test planner.

        Args:
            llm_client: LLM client instance
        """
        self.llm = llm_client
        self.test_suite_catalog = self._load_test_suite_catalog()

    def _load_test_suite_catalog(self) -> Dict[str, Any]:
        """
        Load catalog of available test suites.

        Returns:
            Dictionary mapping test categories to available suites
        """
        return {
            "real_time": {
                "suites": ["rt-tests"],
                "tools": ["cyclictest", "pi_stress", "deadline_test"],
                "capabilities": [
                    "latency_measurement",
                    "scheduling_analysis",
                    "smi_detection",
                    "priority_inheritance"
                ]
            },
            "stress": {
                "suites": ["stress-ng"],
                "tools": ["memory", "network", "filesystem"],
                "capabilities": [
                    "memory_bandwidth",
                    "network_throughput",
                    "io_performance",
                    "system_stability"
                ]
            },
            "network": {
                "suites": ["iperf3", "netperf", "qperf"],
                "tools": ["tcp", "udp", "rdma"],
                "capabilities": [
                    "throughput_testing",
                    "latency_testing",
                    "connection_scaling",
                    "protocol_testing"
                ]
            },
            "io": {
                "suites": ["fio", "iozone", "lmbench"],
                "tools": ["sequential", "random", "sync", "async"],
                "capabilities": [
                    "iops_measurement",
                    "bandwidth_measurement",
                    "latency_analysis",
                    "filesystem_performance"
                ]
            },
            "memory": {
                "suites": ["stream", "memtester", "memory-analysis"],
                "tools": ["bandwidth", "latency", "validation"],
                "capabilities": [
                    "bandwidth_testing",
                    "error_detection",
                    "numa_analysis",
                    "cache_performance"
                ]
            },
            "ebpf": {
                "suites": ["bcc", "bpftrace", "ebpf", "perf"],
                "tools": ["tracing", "profiling", "analysis"],
                "capabilities": [
                    "system_call_tracing",
                    "function_profiling",
                    "network_analysis",
                    "io_tracing"
                ]
            },
            "benchmark": {
                "suites": ["unixbench", "lmbench", "stressapptest"],
                "tools": ["comprehensive", "micro", "hardware"],
                "capabilities": [
                    "system_scoring",
                    "micro_benchmarks",
                    "hardware_validation"
                ]
            },
            "functionality": {
                "suites": ["ltp", "cgroup", "namespace", "security"],
                "tools": ["syscall", "resource", "isolation", "security"],
                "capabilities": [
                    "syscall_validation",
                    "resource_control",
                    "namespace_isolation",
                    "security_testing"
                ]
            }
        }

    def design(
        self,
        requirement: str,
        system_info: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Design test plan based on requirements.

        Args:
            requirement: Natural language requirement
            system_info: System specifications
            constraints: Optional constraints (time, resources, etc.)

        Returns:
            Comprehensive test plan
        """
        # Prepare context for LLM
        context = {
            "requirement": requirement,
            "system_info": system_info,
            "available_suites": self.test_suite_catalog,
            "constraints": constraints or {}
        }

        # Generate test plan using LLM
        prompt = TEST_DESIGN_PROMPT.format(**context)
        response = self.llm.generate(prompt)

        # Parse LLM response into structured test plan
        test_plan = self._parse_test_plan(response)

        # Validate and enrich test plan
        test_plan = self._validate_and_enrich(test_plan, system_info)

        return test_plan

    def _parse_test_plan(self, llm_response: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured test plan.

        Args:
            llm_response: Raw LLM response

        Returns:
            Structured test plan dictionary
        """
        # This would parse the LLM's JSON or structured output
        # For now, return a template structure
        import json
        try:
            plan = json.loads(llm_response)
        except json.JSONDecodeError:
            # If LLM didn't return valid JSON, use fallback
            plan = {
                "summary": "Generated test plan",
                "test_cases": [],
                "estimated_duration": "unknown"
            }

        return plan

    def _validate_and_enrich(
        self,
        test_plan: Dict[str, Any],
        system_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate test plan and add system-specific parameters.

        Args:
            test_plan: Initial test plan
            system_info: System specifications

        Returns:
            Validated and enriched test plan
        """
        # Add system-specific parameters
        test_plan["system_info"] = system_info

        # Validate test cases
        for test_case in test_plan.get("test_cases", []):
            self._validate_test_case(test_case, system_info)

        # Calculate dependencies
        test_plan["execution_order"] = self._calculate_execution_order(
            test_plan.get("test_cases", [])
        )

        return test_plan

    def _validate_test_case(
        self,
        test_case: Dict[str, Any],
        system_info: Dict[str, Any]
    ) -> bool:
        """
        Validate individual test case.

        Args:
            test_case: Test case specification
            system_info: System specifications

        Returns:
            True if valid, raises ValueError otherwise
        """
        required_fields = ["name", "suite", "parameters"]
        for field in required_fields:
            if field not in test_case:
                raise ValueError(f"Test case missing required field: {field}")

        # Validate suite exists
        suite = test_case["suite"]
        if not self._is_suite_available(suite):
            raise ValueError(f"Test suite not available: {suite}")

        return True

    def _is_suite_available(self, suite_name: str) -> bool:
        """Check if test suite is available."""
        for category in self.test_suite_catalog.values():
            if suite_name in category["suites"]:
                return True
        return False

    def _calculate_execution_order(
        self,
        test_cases: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Calculate optimal execution order considering dependencies.

        Args:
            test_cases: List of test cases

        Returns:
            Ordered list of test case names
        """
        # Simple ordering for now - can be enhanced with dependency resolution
        order = []
        for test_case in test_cases:
            order.append(test_case["name"])
        return order

    def get_suite_info(self, suite_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific test suite.

        Args:
            suite_name: Name of the suite

        Returns:
            Suite information or None if not found
        """
        for category, info in self.test_suite_catalog.items():
            if suite_name in info["suites"]:
                return {
                    "category": category,
                    "name": suite_name,
                    "tools": info["tools"],
                    "capabilities": info["capabilities"]
                }
        return None
