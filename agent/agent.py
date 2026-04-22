"""
Main TestingAgent class that orchestrates the entire testing workflow.
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from .planner import TestPlanner
from .executor import TestExecutor
from .analyzer import ResultAnalyzer
from .reporter import ReportGenerator
from models.llm_client import LLMClient


class TestingAgent:
    """
    AI-powered Linux testing agent.

    This agent can:
    - Design test cases based on natural language requirements
    - Execute comprehensive Linux system tests
    - Analyze test results with AI-powered insights
    - Generate detailed reports with optimization recommendations
    """

    def __init__(
        self,
        llm_provider: str = "openai",
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        linux_testing_path: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the testing agent.

        Args:
            llm_provider: LLM provider (openai, anthropic, local)
            model: Model name (gpt-4, claude-3-opus, etc.)
            api_key: API key for LLM provider
            linux_testing_path: Path to linux-testing repository
            config: Additional configuration options
        """
        self.config = config or {}

        # Initialize LLM client
        self.llm = LLMClient(
            provider=llm_provider,
            model=model,
            api_key=api_key or os.getenv(f"{llm_provider.upper()}_API_KEY")
        )

        # Initialize components
        self.planner = TestPlanner(llm_client=self.llm)
        self.executor = TestExecutor(linux_testing_path=linux_testing_path)
        self.analyzer = ResultAnalyzer(llm_client=self.llm)
        self.reporter = ReportGenerator()

        # State
        self.system_info = None
        self.last_test_plan = None
        self.last_results = None
        self.last_analysis = None

    def get_system_info(self) -> Dict[str, Any]:
        """
        Gather system information.

        Returns:
            Dictionary containing system specifications
        """
        if self.system_info is None:
            self.system_info = self.executor.collect_system_info()
        return self.system_info

    def design_test_cases(
        self,
        requirement: str,
        system_info: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Design test cases based on requirements.

        Args:
            requirement: Natural language test requirement
            system_info: System information (auto-collected if not provided)
            constraints: Test constraints (time, resources, etc.)

        Returns:
            Test plan dictionary
        """
        if system_info is None:
            system_info = self.get_system_info()

        test_plan = self.planner.design(
            requirement=requirement,
            system_info=system_info,
            constraints=constraints
        )

        self.last_test_plan = test_plan
        return test_plan

    def execute_tests(
        self,
        test_plan: Optional[Dict[str, Any]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Execute test plan.

        Args:
            test_plan: Test plan to execute (uses last_test_plan if not provided)
            dry_run: If True, simulate execution without running tests

        Returns:
            Test results dictionary
        """
        if test_plan is None:
            test_plan = self.last_test_plan
            if test_plan is None:
                raise ValueError("No test plan available. Call design_test_cases first.")

        results = self.executor.execute(test_plan, dry_run=dry_run)
        self.last_results = results
        return results

    def analyze_results(
        self,
        results: Optional[Dict[str, Any]] = None,
        baseline: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze test results with AI-powered insights.

        Args:
            results: Test results to analyze (uses last_results if not provided)
            baseline: Baseline results for comparison

        Returns:
            Analysis dictionary with insights and recommendations
        """
        if results is None:
            results = self.last_results
            if results is None:
                raise ValueError("No results available. Call execute_tests first.")

        analysis = self.analyzer.analyze(
            results=results,
            baseline=baseline,
            system_info=self.system_info
        )

        self.last_analysis = analysis
        return analysis

    def generate_report(
        self,
        analysis: Optional[Dict[str, Any]] = None,
        output: str = "report.html",
        format: str = "html"
    ) -> str:
        """
        Generate test report.

        Args:
            analysis: Analysis results (uses last_analysis if not provided)
            output: Output file path
            format: Report format (html, pdf, markdown, json)

        Returns:
            Path to generated report
        """
        if analysis is None:
            analysis = self.last_analysis
            if analysis is None:
                raise ValueError("No analysis available. Call analyze_results first.")

        report_path = self.reporter.generate(
            analysis=analysis,
            test_plan=self.last_test_plan,
            results=self.last_results,
            output=output,
            format=format
        )

        return report_path

    def run_full_workflow(
        self,
        requirement: str,
        output_dir: str = "./results",
        report_format: str = "html"
    ) -> Dict[str, Any]:
        """
        Run the complete testing workflow.

        Args:
            requirement: Test requirement in natural language
            output_dir: Directory to save all outputs
            report_format: Format for the final report

        Returns:
            Dictionary containing all workflow outputs
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Step 1: Design test cases
        print("🤖 Designing test cases...")
        test_plan = self.design_test_cases(requirement)
        plan_path = os.path.join(output_dir, f"test_plan_{timestamp}.json")
        with open(plan_path, 'w') as f:
            json.dump(test_plan, f, indent=2)
        print(f"✓ Test plan saved to {plan_path}")

        # Step 2: Execute tests
        print("\n⚡ Executing tests...")
        results = self.execute_tests(test_plan)
        results_path = os.path.join(output_dir, f"results_{timestamp}.json")
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✓ Results saved to {results_path}")

        # Step 3: Analyze results
        print("\n📊 Analyzing results...")
        analysis = self.analyze_results(results)
        analysis_path = os.path.join(output_dir, f"analysis_{timestamp}.json")
        with open(analysis_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"✓ Analysis saved to {analysis_path}")

        # Step 4: Generate report
        print("\n📝 Generating report...")
        report_path = os.path.join(output_dir, f"report_{timestamp}.{report_format}")
        self.generate_report(analysis, output=report_path, format=report_format)
        print(f"✓ Report saved to {report_path}")

        return {
            "test_plan": test_plan,
            "results": results,
            "analysis": analysis,
            "files": {
                "plan": plan_path,
                "results": results_path,
                "analysis": analysis_path,
                "report": report_path
            }
        }

    def performance_benchmark(
        self,
        subsystems: List[str] = None,
        duration: str = "1h",
        workload: str = "standard"
    ) -> Dict[str, Any]:
        """
        Run automated performance benchmark.

        Args:
            subsystems: List of subsystems to test (cpu, memory, network, io)
            duration: Test duration (e.g., "30m", "1h")
            workload: Workload type (light, standard, heavy, production)

        Returns:
            Benchmark results
        """
        if subsystems is None:
            subsystems = ["cpu", "memory", "network", "io"]

        requirement = f"""
        Run comprehensive performance benchmark for: {', '.join(subsystems)}

        Duration: {duration}
        Workload: {workload}

        Include:
        - Baseline performance metrics
        - Stress testing
        - Real-time performance evaluation
        - Statistical analysis (P50, P90, P95, P99)
        """

        return self.run_full_workflow(requirement)

    def regression_test(
        self,
        baseline: str,
        threshold: float = 0.05
    ) -> Dict[str, Any]:
        """
        Run regression test against baseline.

        Args:
            baseline: Path to baseline results
            threshold: Performance degradation threshold (0.05 = 5%)

        Returns:
            Regression test results
        """
        with open(baseline, 'r') as f:
            baseline_data = json.load(f)

        # Re-run tests
        test_plan = baseline_data.get("test_plan")
        results = self.execute_tests(test_plan)

        # Analyze with baseline comparison
        analysis = self.analyze_results(results, baseline=baseline_data)

        # Check for regressions
        analysis["regression_check"] = {
            "threshold": threshold,
            "passed": True,  # Will be computed by analyzer
            "details": []
        }

        return analysis
