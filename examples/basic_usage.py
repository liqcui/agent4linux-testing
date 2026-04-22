#!/usr/bin/env python3
"""
Basic usage example for Agent4Linux-Testing.

This example demonstrates how to use the testing agent to:
1. Design test cases from requirements
2. Execute tests
3. Analyze results
4. Generate reports
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import TestingAgent


def main():
    """
    Main example function.
    """
    print("=" * 60)
    print("Agent4Linux-Testing - Basic Usage Example")
    print("=" * 60)
    print()

    # Initialize the agent
    # Note: Set OPENAI_API_KEY environment variable or pass api_key parameter
    print("🤖 Initializing testing agent...")
    agent = TestingAgent(
        llm_provider="openai",  # or "anthropic", "local"
        model="gpt-4",
        # api_key="your-api-key-here"  # Optional if env var is set
    )
    print("✓ Agent initialized")
    print()

    # Example 1: Simple performance test
    print("=" * 60)
    print("Example 1: Simple Performance Benchmark")
    print("=" * 60)
    print()

    requirement = """
    I need to evaluate the baseline performance of my Linux server.
    Please run comprehensive benchmarks for:
    - CPU performance
    - Memory bandwidth
    - Disk I/O
    - Network throughput

    Duration: 30 minutes
    """

    print("📝 Requirement:")
    print(requirement)
    print()

    # Design test cases
    print("🎯 Designing test plan...")
    test_plan = agent.design_test_cases(requirement)
    print(f"✓ Test plan created with {len(test_plan.get('test_cases', []))} test cases")
    print()

    # Execute tests (dry run for demonstration)
    print("⚡ Executing tests (DRY RUN)...")
    results = agent.execute_tests(test_plan, dry_run=True)
    print(f"✓ Tests executed: {results['summary']}")
    print()

    # Analyze results
    print("📊 Analyzing results...")
    analysis = agent.analyze_results(results)
    print(f"✓ Analysis complete")
    print(f"  Verdict: {analysis['verdict']}")
    print(f"  Score: {analysis['score']:.1f}/100")
    print()

    # Generate report
    print("📝 Generating report...")
    report_path = agent.generate_report(
        analysis,
        output="example_report.html",
        format="html"
    )
    print(f"✓ Report generated: {report_path}")
    print()

    # Example 2: Real-time performance test
    print("=" * 60)
    print("Example 2: Real-time Performance Evaluation")
    print("=" * 60)
    print()

    rt_requirement = """
    Test real-time performance with the following requirements:
    - Maximum latency < 100μs
    - P99 latency < 50μs
    - Test under CPU stress (80% load)

    Use cyclictest and stress-ng.
    """

    print("📝 Requirement:")
    print(rt_requirement)
    print()

    # Run full workflow
    print("🚀 Running full testing workflow...")
    workflow_result = agent.run_full_workflow(
        requirement=rt_requirement,
        output_dir="./example_results",
        report_format="html"
    )

    print("✓ Workflow complete!")
    print(f"  Files generated:")
    for file_type, path in workflow_result["files"].items():
        print(f"    - {file_type}: {path}")
    print()

    # Example 3: Regression test
    print("=" * 60)
    print("Example 3: Regression Testing")
    print("=" * 60)
    print()

    # This would normally use a real baseline file
    print("📊 Regression testing against baseline...")
    print("  (Skipped - requires existing baseline)")
    print()

    # Example 4: Custom test design
    print("=" * 60)
    print("Example 4: Custom Test Scenario")
    print("=" * 60)
    print()

    custom_requirement = """
    Design a test for a web server that needs to handle:
    - 10,000 concurrent connections
    - 1GB/s network throughput
    - Response time < 10ms
    - Zero packet loss

    Test both normal and stressed conditions.
    Include network performance tests and real-time latency checks.
    """

    print("📝 Custom Requirement:")
    print(custom_requirement)
    print()

    print("🎯 Designing custom test...")
    custom_plan = agent.design_test_cases(custom_requirement)
    print("✓ Custom test plan created")
    print(f"  Estimated duration: {custom_plan.get('total_estimated_duration', 'unknown')}")
    print()

    print("=" * 60)
    print("Examples Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review the generated reports")
    print("2. Examine the test plans in detail")
    print("3. Run tests with dry_run=False for real execution")
    print("4. Compare results with your requirements")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
