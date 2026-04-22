"""
Result Analyzer - AI-powered analysis of test results.
"""

from typing import Dict, List, Optional, Any
from models.prompts import ANALYSIS_PROMPT
import statistics


class ResultAnalyzer:
    """
    Analyzes test results and provides insights.

    Uses AI to identify performance issues, anomalies, and optimization opportunities.
    """

    def __init__(self, llm_client):
        """
        Initialize the analyzer.

        Args:
            llm_client: LLM client instance
        """
        self.llm = llm_client
        self.performance_baselines = self._load_performance_baselines()

    def _load_performance_baselines(self) -> Dict[str, Any]:
        """
        Load performance baselines for comparison.

        Returns:
            Dictionary of baseline metrics
        """
        return {
            "real_time": {
                "max_latency_us": {
                    "excellent": 50,
                    "good": 100,
                    "acceptable": 500,
                    "poor": 1000
                }
            },
            "network": {
                "tcp_throughput_gbps": {
                    "excellent": 10,
                    "good": 5,
                    "acceptable": 1
                }
            },
            "io": {
                "iops": {
                    "nvme_excellent": 200000,
                    "sata_excellent": 50000,
                    "hdd_excellent": 200
                }
            }
        }

    def analyze(
        self,
        results: Dict[str, Any],
        baseline: Optional[Dict[str, Any]] = None,
        system_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze test results.

        Args:
            results: Test execution results
            baseline: Optional baseline for comparison
            system_info: System information

        Returns:
            Analysis with insights and recommendations
        """
        analysis = {
            "timestamp": results.get("end_time"),
            "verdict": "unknown",
            "score": 0.0,
            "insights": [],
            "bottlenecks": [],
            "recommendations": [],
            "statistical_analysis": {},
            "baseline_comparison": None
        }

        # Statistical analysis
        analysis["statistical_analysis"] = self._statistical_analysis(results)

        # Performance rating
        analysis["performance_rating"] = self._rate_performance(results)

        # Identify bottlenecks
        analysis["bottlenecks"] = self._identify_bottlenecks(results)

        # Baseline comparison
        if baseline:
            analysis["baseline_comparison"] = self._compare_with_baseline(
                results,
                baseline
            )

        # Generate AI-powered insights
        analysis["insights"] = self._generate_insights(
            results,
            analysis,
            system_info
        )

        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(
            results,
            analysis
        )

        # Overall verdict
        analysis["verdict"] = self._determine_verdict(analysis)

        # Calculate overall score
        analysis["score"] = self._calculate_score(analysis)

        return analysis

    def _statistical_analysis(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform statistical analysis on metrics.

        Args:
            results: Test results

        Returns:
            Statistical analysis
        """
        stats = {
            "metrics": {},
            "summary": {}
        }

        # Collect all metrics
        all_metrics = {}
        for test_case in results.get("test_cases", []):
            for metric_name, value in test_case.get("metrics", {}).items():
                if metric_name not in all_metrics:
                    all_metrics[metric_name] = []
                all_metrics[metric_name].append(value)

        # Calculate statistics for each metric
        for metric_name, values in all_metrics.items():
            if values and all(isinstance(v, (int, float)) for v in values):
                stats["metrics"][metric_name] = {
                    "min": min(values),
                    "max": max(values),
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "stdev": statistics.stdev(values) if len(values) > 1 else 0
                }

        return stats

    def _rate_performance(self, results: Dict[str, Any]) -> Dict[str, str]:
        """
        Rate performance of each test case.

        Args:
            results: Test results

        Returns:
            Performance ratings
        """
        ratings = {}

        for test_case in results.get("test_cases", []):
            suite = test_case.get("suite")
            metrics = test_case.get("metrics", {})

            rating = "unknown"

            # Suite-specific rating logic
            if suite == "rt-tests" and "max_latency_us" in metrics:
                latency = metrics["max_latency_us"]
                if latency < 50:
                    rating = "excellent"
                elif latency < 100:
                    rating = "good"
                elif latency < 500:
                    rating = "acceptable"
                else:
                    rating = "poor"

            ratings[test_case["name"]] = rating

        return ratings

    def _identify_bottlenecks(self, results: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Identify performance bottlenecks.

        Args:
            results: Test results

        Returns:
            List of identified bottlenecks
        """
        bottlenecks = []

        for test_case in results.get("test_cases", []):
            if test_case.get("status") == "failed":
                bottlenecks.append({
                    "type": "failure",
                    "test": test_case["name"],
                    "description": f"Test {test_case['name']} failed"
                })

            # Check for poor performance
            metrics = test_case.get("metrics", {})
            if "max_latency_us" in metrics and metrics["max_latency_us"] > 500:
                bottlenecks.append({
                    "type": "high_latency",
                    "test": test_case["name"],
                    "description": f"High latency detected: {metrics['max_latency_us']}μs"
                })

        return bottlenecks

    def _compare_with_baseline(
        self,
        results: Dict[str, Any],
        baseline: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare results with baseline.

        Args:
            results: Current results
            baseline: Baseline results

        Returns:
            Comparison analysis
        """
        comparison = {
            "improvements": [],
            "regressions": [],
            "stable": []
        }

        # This would compare metrics from results vs baseline
        # Simplified implementation for now

        return comparison

    def _generate_insights(
        self,
        results: Dict[str, Any],
        analysis: Dict[str, Any],
        system_info: Optional[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate AI-powered insights.

        Args:
            results: Test results
            analysis: Preliminary analysis
            system_info: System information

        Returns:
            List of insights
        """
        # Prepare context for LLM
        context = {
            "results": results,
            "analysis": analysis,
            "system_info": system_info or {}
        }

        prompt = ANALYSIS_PROMPT.format(**context)
        response = self.llm.generate(prompt)

        # Parse insights from LLM response
        # For now, return some basic insights
        insights = []

        summary = results.get("summary", {})
        if summary.get("failed", 0) > 0:
            insights.append(
                f"⚠ {summary['failed']} test(s) failed out of {summary['total']}"
            )

        if analysis.get("bottlenecks"):
            insights.append(
                f"🔍 Detected {len(analysis['bottlenecks'])} performance bottleneck(s)"
            )

        return insights

    def _generate_recommendations(
        self,
        results: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Generate optimization recommendations.

        Args:
            results: Test results
            analysis: Analysis results

        Returns:
            List of recommendations
        """
        recommendations = []

        # Based on bottlenecks
        for bottleneck in analysis.get("bottlenecks", []):
            if bottleneck["type"] == "high_latency":
                recommendations.append({
                    "category": "real_time",
                    "priority": "high",
                    "description": "Consider installing PREEMPT_RT kernel for better real-time performance",
                    "commands": [
                        "sudo apt-get install linux-image-rt-amd64"
                    ]
                })

        # Based on test failures
        if results.get("summary", {}).get("failed", 0) > 0:
            recommendations.append({
                "category": "testing",
                "priority": "high",
                "description": "Investigate and fix failing tests before production deployment"
            })

        return recommendations

    def _determine_verdict(self, analysis: Dict[str, Any]) -> str:
        """
        Determine overall test verdict.

        Args:
            analysis: Analysis results

        Returns:
            Verdict string (PASS, FAIL, WARNING)
        """
        if analysis.get("bottlenecks"):
            return "WARNING"

        ratings = analysis.get("performance_rating", {})
        if any(r == "poor" for r in ratings.values()):
            return "FAIL"

        if all(r in ["excellent", "good"] for r in ratings.values()):
            return "PASS"

        return "WARNING"

    def _calculate_score(self, analysis: Dict[str, Any]) -> float:
        """
        Calculate overall performance score.

        Args:
            analysis: Analysis results

        Returns:
            Score from 0.0 to 100.0
        """
        # Simple scoring based on performance ratings
        rating_scores = {
            "excellent": 100,
            "good": 80,
            "acceptable": 60,
            "poor": 40,
            "unknown": 50
        }

        ratings = analysis.get("performance_rating", {})
        if not ratings:
            return 50.0

        scores = [rating_scores.get(r, 50) for r in ratings.values()]
        return sum(scores) / len(scores)
