#!/usr/bin/env python3
"""
Command-line interface for Agent4Linux-Testing.
"""

import sys
import os
import json
import argparse

from agent import TestingAgent


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI-powered Linux testing automation"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Design command
    design_parser = subparsers.add_parser("design", help="Design test cases")
    design_parser.add_argument("--requirement", required=True, help="Test requirement")
    design_parser.add_argument("--output", default="test_plan.json", help="Output file")

    # Execute command
    exec_parser = subparsers.add_parser("execute", help="Execute tests")
    exec_parser.add_argument("--plan", required=True, help="Test plan file")
    exec_parser.add_argument("--output", default="results.json", help="Output file")
    exec_parser.add_argument("--dry-run", action="store_true", help="Simulate execution")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze results")
    analyze_parser.add_argument("--results", required=True, help="Results file")
    analyze_parser.add_argument("--output", default="analysis.json", help="Output file")
    analyze_parser.add_argument("--baseline", help="Baseline file for comparison")

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate report")
    report_parser.add_argument("--analysis", required=True, help="Analysis file")
    report_parser.add_argument("--format", default="html", choices=["html", "markdown", "json"])
    report_parser.add_argument("--output", help="Output file")

    # Run command (full workflow)
    run_parser = subparsers.add_parser("run", help="Run full workflow")
    run_parser.add_argument("--requirement", required=True, help="Test requirement")
    run_parser.add_argument("--output-dir", default="./results", help="Output directory")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Initialize agent
    agent = TestingAgent()

    try:
        if args.command == "design":
            print(f"🎯 Designing test cases for: {args.requirement}")
            plan = agent.design_test_cases(args.requirement)
            with open(args.output, 'w') as f:
                json.dump(plan, f, indent=2)
            print(f"✓ Test plan saved to {args.output}")

        elif args.command == "execute":
            print(f"⚡ Executing test plan: {args.plan}")
            with open(args.plan) as f:
                plan = json.load(f)
            results = agent.execute_tests(plan, dry_run=args.dry_run)
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"✓ Results saved to {args.output}")

        elif args.command == "analyze":
            print(f"📊 Analyzing results: {args.results}")
            with open(args.results) as f:
                results = json.load(f)
            baseline = None
            if args.baseline:
                with open(args.baseline) as f:
                    baseline = json.load(f)
            analysis = agent.analyze_results(results, baseline=baseline)
            with open(args.output, 'w') as f:
                json.dump(analysis, f, indent=2)
            print(f"✓ Analysis saved to {args.output}")
            print(f"  Verdict: {analysis['verdict']}")
            print(f"  Score: {analysis['score']:.1f}/100")

        elif args.command == "report":
            print(f"📝 Generating {args.format} report...")
            with open(args.analysis) as f:
                analysis = json.load(f)

            if not args.output:
                args.output = f"report.{args.format}"

            report_path = agent.generate_report(
                analysis,
                output=args.output,
                format=args.format
            )
            print(f"✓ Report saved to {report_path}")

        elif args.command == "run":
            print(f"🚀 Running full workflow...")
            result = agent.run_full_workflow(
                requirement=args.requirement,
                output_dir=args.output_dir
            )
            print("\n✓ Workflow complete!")
            print(f"  Verdict: {result['analysis']['verdict']}")
            print(f"  Score: {result['analysis']['score']:.1f}/100")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
