#!/usr/bin/env python3
"""
Advanced usage examples demonstrating Phase 2 features.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import TestingAgent
from integrations import MetricsCollector, RTTestsParser, NetworkParser
from utils import MetricsVisualizer


def example1_advanced_metrics_collection():
    """
    Example 1: Advanced metrics collection and analysis.
    """
    print("=" * 70)
    print("Example 1: Advanced Metrics Collection")
    print("=" * 70)

    # Initialize metrics collector
    collector = MetricsCollector()

    # Simulate collecting metrics from multiple test runs
    print("\n📊 Collecting metrics from multiple test runs...")

    # RT latency metrics
    for i in range(10):
        collector.add_metric(
            name="max_latency",
            value=50 + i * 2,
            unit="us",
            category="real_time",
            tags={"test": "cyclictest", "run": str(i)}
        )

    # Network throughput metrics
    for i in range(10):
        collector.add_metric(
            name="throughput",
            value=950 + i * 5,
            unit="Mbps",
            category="network",
            tags={"test": "iperf3", "run": str(i)}
        )

    # Get statistics
    print("\n📈 Statistical Analysis:")
    latency_stats = collector.get_statistics("max_latency")
    if latency_stats:
        print(f"\nMax Latency Statistics:")
        print(f"  Mean:   {latency_stats['mean']:.2f} us")
        print(f"  Median: {latency_stats['median']:.2f} us")
        print(f"  Min:    {latency_stats['min']:.2f} us")
        print(f"  Max:    {latency_stats['max']:.2f} us")
        print(f"  P95:    {latency_stats['p95']:.2f} us")
        print(f"  P99:    {latency_stats['p99']:.2f} us")

    throughput_stats = collector.get_statistics("throughput")
    if throughput_stats:
        print(f"\nThroughput Statistics:")
        print(f"  Mean:   {throughput_stats['mean']:.2f} Mbps")
        print(f"  Median: {throughput_stats['median']:.2f} Mbps")
        print(f"  Min:    {throughput_stats['min']:.2f} Mbps")
        print(f"  Max:    {throughput_stats['max']:.2f} Mbps")

    # Generate summary
    summary = collector.generate_summary()
    print(f"\n📋 Summary: {summary['total_metrics']} unique metrics")
    print(f"   Categories: {', '.join(summary['categories'])}")


def example2_baseline_comparison():
    """
    Example 2: Baseline comparison and regression detection.
    """
    print("\n" + "=" * 70)
    print("Example 2: Baseline Comparison & Regression Detection")
    print("=" * 70)

    # Create baseline metrics
    baseline = MetricsCollector()
    baseline.add_metric("max_latency", 45.0, "us", "real_time")
    baseline.add_metric("avg_latency", 12.0, "us", "real_time")
    baseline.add_metric("throughput", 950.0, "Mbps", "network")
    baseline.add_metric("iops", 50000.0, "ops/s", "io")

    # Create current metrics (with some regressions)
    current = MetricsCollector()
    current.add_metric("max_latency", 65.0, "us", "real_time")  # Regression
    current.add_metric("avg_latency", 10.0, "us", "real_time")  # Improvement
    current.add_metric("throughput", 980.0, "Mbps", "network")  # Improvement
    current.add_metric("iops", 48000.0, "ops/s", "io")         # Slight regression

    print("\n🔍 Comparing current results with baseline (5% threshold)...")

    comparison = current.compare_with_baseline(baseline, threshold=0.05)

    print(f"\n❌ Regressions: {len(comparison['regressions'])}")
    for reg in comparison['regressions']:
        print(f"   - {reg['metric']}: {reg['baseline_mean']:.2f} → {reg['current_mean']:.2f} "
              f"({reg['change_percent']:+.1f}%)")

    print(f"\n✅ Improvements: {len(comparison['improvements'])}")
    for imp in comparison['improvements']:
        print(f"   + {imp['metric']}: {imp['baseline_mean']:.2f} → {imp['current_mean']:.2f} "
              f"({imp['change_percent']:+.1f}%)")

    print(f"\n➡️  Stable: {len(comparison['stable'])}")
    for stable in comparison['stable']:
        print(f"   = {stable['metric']}: {stable['baseline_mean']:.2f} → {stable['current_mean']:.2f}")


def example3_parser_integration():
    """
    Example 3: Using advanced parsers for test output.
    """
    print("\n" + "=" * 70)
    print("Example 3: Advanced Parser Integration")
    print("=" * 70)

    # Example cyclictest output
    cyclictest_output = """
T: 0 ( 1234) P:99 I:1000 C:  60000 Min:   2 Act:   5 Avg:   6 Max:  18
T: 1 ( 1235) P:99 I:1000 C:  60000 Min:   3 Act:   4 Avg:   7 Max:  22
T: 2 ( 1236) P:99 I:1000 C:  60000 Min:   2 Act:   6 Avg:   8 Max:  25
Min Latencies: 2
Avg Latencies: 7
Max Latencies: 25
"""

    print("\n🔧 Parsing cyclictest output...")
    parser = RTTestsParser()
    metrics = parser.parse(cyclictest_output)

    print(f"\nParsed Metrics:")
    print(f"  Thread Count: {len(metrics['threads'])}")
    print(f"  Overall Max:  {metrics['statistics']['overall_max']} us")
    print(f"  Overall Avg:  {metrics['statistics']['overall_avg']:.2f} us")
    print(f"  Std Dev:      {metrics['statistics']['max_std_dev']:.2f} us")

    # Example iperf3 output
    iperf3_output = """
[ ID] Interval           Transfer     Bitrate
[SUM]   0.00-10.00  sec  1.10 GBytes  944 Mbits/sec                  sender
[SUM]   0.00-10.00  sec  1.09 GBytes  940 Mbits/sec                  receiver
"""

    print("\n🔧 Parsing iperf3 output...")
    net_parser = NetworkParser()
    net_metrics = net_parser.parse(iperf3_output)

    print(f"\nParsed Network Metrics:")
    print(f"  TX Throughput: {net_metrics['throughput_tx_mbps']:.2f} Mbps")
    print(f"  RX Throughput: {net_metrics['throughput_rx_mbps']:.2f} Mbps")


def example4_visualization():
    """
    Example 4: Metrics visualization.
    """
    print("\n" + "=" * 70)
    print("Example 4: Metrics Visualization")
    print("=" * 70)

    visualizer = MetricsVisualizer(output_dir="./visualizations")

    # Create sample data
    latency_values = [45, 48, 52, 47, 49, 51, 46, 50, 53, 48]
    percentiles = {"p50": 48, "p90": 52, "p95": 53, "p99": 53}

    print("\n📊 Generating visualizations...")

    # Create line chart
    chart1 = visualizer.create_metric_chart(
        metric_name="latency",
        values=latency_values,
        chart_type="line",
        title="Latency Over Time",
        unit="us"
    )
    print(f"  ✓ Line chart: {chart1}")

    # Create histogram
    chart2 = visualizer.create_metric_chart(
        metric_name="latency_distribution",
        values=latency_values,
        chart_type="histogram",
        title="Latency Distribution",
        unit="us"
    )
    print(f"  ✓ Histogram: {chart2}")

    # Create percentile chart
    chart3 = visualizer.create_percentile_chart(
        metric_name="latency",
        percentiles=percentiles,
        title="Latency Percentiles",
        unit="us"
    )
    print(f"  ✓ Percentile chart: {chart3}")

    # Create comparison chart
    baseline_metrics = {"max_latency": 45, "avg_latency": 12, "throughput": 950}
    current_metrics = {"max_latency": 48, "avg_latency": 11, "throughput": 980}

    chart4 = visualizer.create_comparison_chart(
        baseline=baseline_metrics,
        current=current_metrics,
        title="Baseline vs Current"
    )
    print(f"  ✓ Comparison chart: {chart4}")


def example5_end_to_end_with_llm():
    """
    Example 5: End-to-end workflow with actual LLM integration.
    """
    print("\n" + "=" * 70)
    print("Example 5: End-to-End Workflow with LLM")
    print("=" * 70)

    # Check if API key is available
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        print("\n⚠️  No API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        print("   This example will run with fallback mode (limited functionality)")

    # Initialize agent
    agent = TestingAgent()

    requirement = """
    Test server real-time performance:
    - Maximum latency < 100 microseconds
    - P99 latency < 50 microseconds
    - Test under moderate CPU load (50%)
    - Duration: 5 minutes
    """

    print(f"\n🎯 Requirement:\n{requirement}")
    print("\n🤖 Designing test plan with AI...")

    # Design test cases
    test_plan = agent.design_test_cases(requirement)

    print(f"\n📋 Generated {len(test_plan.get('test_cases', []))} test cases:")
    for tc in test_plan.get('test_cases', [])[:3]:
        print(f"   - {tc['name']} ({tc['suite']})")

    print("\n💡 For full execution, run:")
    print("   python -m agent4linux run --requirement \"<your requirement>\"")


def main():
    """Run all examples."""
    print("\n🚀 Agent4Linux-Testing - Advanced Usage Examples (Phase 2)")
    print("=" * 70)

    try:
        example1_advanced_metrics_collection()
        example2_baseline_comparison()
        example3_parser_integration()
        example4_visualization()
        example5_end_to_end_with_llm()

        print("\n" + "=" * 70)
        print("✅ All examples completed successfully!")
        print("\nNext steps:")
        print("  1. Explore the generated visualizations in ./visualizations/")
        print("  2. Try running with your own test requirements")
        print("  3. Set up API keys for full LLM integration")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
