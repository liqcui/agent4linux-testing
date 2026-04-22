#!/usr/bin/env python3
"""
Phase 3 usage examples: Dashboard, Historical tracking, CI/CD integration.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def example1_start_dashboard():
    """
    Example 1: Start web dashboard.
    """
    print("=" * 70)
    print("Example 1: Web Dashboard")
    print("=" * 70)

    from dashboard import DashboardServer

    # Initialize dashboard server
    server = DashboardServer(
        host="0.0.0.0",
        port=5000,
        data_dir="./test_results"
    )

    print("\n🚀 Starting web dashboard...")
    print("   Dashboard URL: http://localhost:5000")
    print("   Press Ctrl+C to stop\n")

    try:
        # Start in foreground
        server.start(debug=True, background=False)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping dashboard...")
        server.stop()


def example2_historical_tracking():
    """
    Example 2: Historical data tracking and analysis.
    """
    print("\n" + "=" * 70)
    print("Example 2: Historical Tracking")
    print("=" * 70)

    from history import HistoryTracker

    # Initialize tracker
    tracker = HistoryTracker(db_path="./test_history.db")

    # Simulate recording test runs
    print("\n📊 Recording test runs to history database...")

    test_run = {
        'test_id': f'test_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'timestamp': datetime.now().isoformat(),
        'requirement': 'System performance baseline',
        'status': 'completed',
        'verdict': 'PASS',
        'score': 85.5,
        'duration': 300.0,
        'test_cases': [
            {
                'name': 'CPU Performance',
                'suite': 'stress-ng',
                'status': 'completed',
                'start_time': datetime.now().isoformat(),
                'end_time': datetime.now().isoformat(),
                'metrics': {
                    'max_latency': 45.2,
                    'throughput': 950.0,
                    'iops': 50000
                }
            }
        ]
    }

    run_id = tracker.record_test_run(test_run)
    print(f"   ✓ Recorded test run ID: {run_id}")

    # Get recent runs
    print("\n📋 Recent test runs:")
    recent = tracker.get_recent_runs(limit=5)
    for run in recent:
        print(f"   - {run['test_id']}: {run['verdict']} (Score: {run['score']})")

    # Analyze trends
    print("\n📈 Analyzing latency trend...")
    trend = tracker.get_metric_trend('max_latency', days=7)
    print(f"   Trend: {trend['trend']}")
    print(f"   Current Avg: {trend['current_avg']:.2f}")
    print(f"   Data points: {trend['data_points']}")

    # Create baseline
    print("\n💾 Creating baseline...")
    baseline_id = tracker.create_baseline_from_run(
        test_run['test_id'],
        'baseline-main',
        'Main branch baseline'
    )
    print(f"   ✓ Created baseline ID: {baseline_id}")

    # Performance summary
    print("\n📊 Performance summary (last 30 days):")
    summary = tracker.get_performance_summary(days=30)
    print(f"   Total runs: {summary['total_runs']}")
    print(f"   Pass rate: {summary['pass_rate']:.1f}%")
    print(f"   Avg score: {summary['avg_score']:.1f}")

    tracker.close()


def example3_cicd_integration():
    """
    Example 3: Generate CI/CD configuration files.
    """
    print("\n" + "=" * 70)
    print("Example 3: CI/CD Integration")
    print("=" * 70)

    from cicd import GitHubActionsIntegration, JenkinsIntegration, GitLabCIIntegration

    print("\n🔧 Generating CI/CD configuration files...")

    # GitHub Actions
    print("\n   GitHub Actions:")
    workflow_path = GitHubActionsIntegration.generate_workflow(
        name="Linux Performance Testing",
        schedule="0 0 * * *",  # Daily at midnight
        output_path=".github/workflows/performance-test.yml"
    )
    print(f"   ✓ Generated: {workflow_path}")

    baseline_workflow = GitHubActionsIntegration.generate_baseline_workflow(
        output_path=".github/workflows/create-baseline.yml"
    )
    print(f"   ✓ Generated: {baseline_workflow}")

    # Jenkins
    print("\n   Jenkins:")
    jenkinsfile = JenkinsIntegration.generate_jenkinsfile(
        cron_schedule="H 0 * * *",
        output_path="Jenkinsfile"
    )
    print(f"   ✓ Generated: {jenkinsfile}")

    baseline_job = JenkinsIntegration.generate_baseline_job(
        output_path="Jenkinsfile.baseline"
    )
    print(f"   ✓ Generated: {baseline_job}")

    # GitLab CI
    print("\n   GitLab CI:")
    gitlab_ci = GitLabCIIntegration.generate_gitlab_ci(
        output_path=".gitlab-ci.yml"
    )
    print(f"   ✓ Generated: {gitlab_ci}")

    print("\n📝 Configuration files generated successfully!")
    print("\nNext steps:")
    print("  1. Review and customize the generated files")
    print("  2. Set up API keys as secrets in your CI/CD platform")
    print("  3. Commit the files to your repository")
    print("  4. Configure triggers and notifications")


def example4_end_to_end_workflow():
    """
    Example 4: Complete workflow with all Phase 3 features.
    """
    print("\n" + "=" * 70)
    print("Example 4: End-to-End Workflow")
    print("=" * 70)

    from agent import TestingAgent
    from history import HistoryTracker
    from dashboard import DashboardServer

    print("\n🔄 Running complete workflow...")

    # Initialize components
    agent = TestingAgent()
    tracker = HistoryTracker()

    # Run test
    print("\n1️⃣ Running performance test...")
    requirement = "Test baseline CPU and memory performance"

    test_plan = agent.design_test_cases(requirement)
    print(f"   ✓ Test plan created with {len(test_plan.get('test_cases', []))} cases")

    # Note: Actual execution would be done here
    # results = agent.execute_tests(test_plan)

    # Simulate results for demo
    results = {
        'test_id': f'test_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'timestamp': datetime.now().isoformat(),
        'requirement': requirement,
        'status': 'completed',
        'verdict': 'PASS',
        'score': 87.5,
        'duration': 180.0,
        'test_cases': [
            {
                'name': 'CPU Performance',
                'suite': 'stress-ng',
                'status': 'completed',
                'start_time': datetime.now().isoformat(),
                'end_time': datetime.now().isoformat(),
                'metrics': {
                    'max_latency': 42.5,
                    'throughput': 980.0
                }
            }
        ]
    }

    print(f"   ✓ Test completed: {results['verdict']} (Score: {results['score']})")

    # Record to history
    print("\n2️⃣ Recording to history database...")
    run_id = tracker.record_test_run(results)
    print(f"   ✓ Recorded run ID: {run_id}")

    # Analyze trends
    print("\n3️⃣ Analyzing trends...")
    trend = tracker.get_metric_trend('max_latency', days=7)
    print(f"   ✓ Latency trend: {trend['trend']}")

    # Export report
    print("\n4️⃣ Exporting historical data...")
    tracker.export_to_json('historical_data.json', days=30)
    print("   ✓ Exported to historical_data.json")

    print("\n5️⃣ Dashboard would display:")
    print("   - Real-time test results")
    print("   - Performance trends over time")
    print("   - Regression analysis")
    print("   - Baseline comparisons")

    print("\n✅ Workflow complete!")

    tracker.close()


def main():
    """Run Phase 3 examples."""
    print("\n🚀 Agent4Linux-Testing - Phase 3 Examples")
    print("Web Dashboard | Historical Tracking | CI/CD Integration")
    print("=" * 70)

    import argparse

    parser = argparse.ArgumentParser(description="Phase 3 Examples")
    parser.add_argument('--example', type=int, choices=[1, 2, 3, 4],
                       help='Run specific example (1-4)')
    parser.add_argument('--dashboard', action='store_true',
                       help='Start web dashboard (Example 1)')

    args = parser.parse_args()

    try:
        if args.dashboard or args.example == 1:
            example1_start_dashboard()
        elif args.example == 2:
            example2_historical_tracking()
        elif args.example == 3:
            example3_cicd_integration()
        elif args.example == 4:
            example4_end_to_end_workflow()
        else:
            # Run all except dashboard
            example2_historical_tracking()
            example3_cicd_integration()
            example4_end_to_end_workflow()

            print("\n" + "=" * 70)
            print("✅ All examples completed!")
            print("\nTo start the web dashboard, run:")
            print("   python examples/phase3_usage.py --dashboard")
            print("=" * 70)

    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
