"""
Report Generator - Creates comprehensive test reports.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import json
import os

# Import visualizer
from utils import MetricsVisualizer


class ReportGenerator:
    """
    Generates test reports in various formats.

    Supports HTML, PDF, Markdown, and JSON formats.
    """

    def __init__(self):
        """Initialize report generator."""
        self.visualizer = MetricsVisualizer()

    def generate(
        self,
        analysis: Dict[str, Any],
        test_plan: Dict[str, Any],
        results: Dict[str, Any],
        output: str = "report.html",
        format: str = "html"
    ) -> str:
        """
        Generate test report.

        Args:
            analysis: Analysis results
            test_plan: Test plan
            results: Test results
            output: Output file path
            format: Report format (html, pdf, markdown, json)

        Returns:
            Path to generated report
        """
        if format == "html":
            return self._generate_html(analysis, test_plan, results, output)
        elif format == "markdown":
            return self._generate_markdown(analysis, test_plan, results, output)
        elif format == "json":
            return self._generate_json(analysis, test_plan, results, output)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_html(
        self,
        analysis: Dict[str, Any],
        test_plan: Dict[str, Any],
        results: Dict[str, Any],
        output: str
    ) -> str:
        """Generate HTML report."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Linux Testing Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .verdict {{
            font-size: 24px;
            font-weight: bold;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            margin: 20px 0;
        }}
        .verdict.PASS {{ background-color: #4caf50; color: white; }}
        .verdict.FAIL {{ background-color: #f44336; color: white; }}
        .verdict.WARNING {{ background-color: #ff9800; color: white; }}
        .section {{
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric {{
            display: inline-block;
            margin: 10px;
            padding: 15px;
            background: #f0f0f0;
            border-radius: 5px;
            min-width: 150px;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}
        .metric-label {{
            font-size: 14px;
            color: #666;
        }}
        .recommendation {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin: 10px 0;
        }}
        .bottleneck {{
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 15px;
            margin: 10px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #667eea;
            color: white;
        }}
        .status-passed {{ color: #4caf50; font-weight: bold; }}
        .status-failed {{ color: #f44336; font-weight: bold; }}
        .status-error {{ color: #ff9800; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 Linux Testing Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="verdict {analysis['verdict']}">
        {analysis['verdict']}: Score {analysis['score']:.1f}/100
    </div>

    <div class="section">
        <h2>📊 Summary</h2>
        <div class="metric">
            <div class="metric-value">{results['summary']['total']}</div>
            <div class="metric-label">Total Tests</div>
        </div>
        <div class="metric">
            <div class="metric-value">{results['summary']['passed']}</div>
            <div class="metric-label">Passed</div>
        </div>
        <div class="metric">
            <div class="metric-value">{results['summary']['failed']}</div>
            <div class="metric-label">Failed</div>
        </div>
        <div class="metric">
            <div class="metric-value">{results['summary']['success_rate']:.1f}%</div>
            <div class="metric-label">Success Rate</div>
        </div>
    </div>

    <div class="section">
        <h2>🔍 Insights</h2>
        {''.join(f'<p>• {insight}</p>' for insight in analysis.get('insights', []))}
    </div>

    <div class="section">
        <h2>⚠️ Bottlenecks</h2>
        {self._format_bottlenecks_html(analysis.get('bottlenecks', []))}
    </div>

    <div class="section">
        <h2>💡 Recommendations</h2>
        {self._format_recommendations_html(analysis.get('recommendations', []))}
    </div>

    <div class="section">
        <h2>📋 Test Results</h2>
        {self._format_test_results_html(results.get('test_cases', []))}
    </div>
</body>
</html>
"""
        with open(output, 'w') as f:
            f.write(html)

        return output

    def _format_bottlenecks_html(self, bottlenecks: list) -> str:
        """Format bottlenecks for HTML."""
        if not bottlenecks:
            return "<p>✅ No bottlenecks detected</p>"

        html = ""
        for b in bottlenecks:
            html += f"""
            <div class="bottleneck">
                <strong>{b.get('type', 'unknown').replace('_', ' ').title()}:</strong>
                {b.get('description', '')}
            </div>
            """
        return html

    def _format_recommendations_html(self, recommendations: list) -> str:
        """Format recommendations for HTML."""
        if not recommendations:
            return "<p>No specific recommendations</p>"

        html = ""
        for rec in recommendations:
            commands = rec.get('commands', [])
            cmd_html = ""
            if commands:
                cmd_html = "<pre>" + "\n".join(commands) + "</pre>"

            html += f"""
            <div class="recommendation">
                <strong>[{rec.get('priority', 'normal').upper()}] {rec.get('category', '').title()}:</strong>
                <p>{rec.get('description', '')}</p>
                {cmd_html}
            </div>
            """
        return html

    def _format_test_results_html(self, test_cases: list) -> str:
        """Format test results table for HTML."""
        html = "<table><tr><th>Test Name</th><th>Suite</th><th>Status</th><th>Metrics</th></tr>"

        for tc in test_cases:
            status_class = f"status-{tc.get('status', 'unknown')}"
            metrics_str = ", ".join(f"{k}: {v}" for k, v in tc.get('metrics', {}).items())

            html += f"""
            <tr>
                <td>{tc.get('name', 'Unknown')}</td>
                <td>{tc.get('suite', 'Unknown')}</td>
                <td class="{status_class}">{tc.get('status', 'unknown').upper()}</td>
                <td>{metrics_str or 'N/A'}</td>
            </tr>
            """

        html += "</table>"
        return html

    def _generate_markdown(
        self,
        analysis: Dict[str, Any],
        test_plan: Dict[str, Any],
        results: Dict[str, Any],
        output: str
    ) -> str:
        """Generate Markdown report."""
        md = f"""# Linux Testing Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Verdict: {analysis['verdict']}

**Score:** {analysis['score']:.1f}/100

## Summary

- **Total Tests:** {results['summary']['total']}
- **Passed:** {results['summary']['passed']}
- **Failed:** {results['summary']['failed']}
- **Success Rate:** {results['summary']['success_rate']:.1f}%

## Insights

{chr(10).join(f"- {insight}" for insight in analysis.get('insights', []))}

## Bottlenecks

{self._format_bottlenecks_markdown(analysis.get('bottlenecks', []))}

## Recommendations

{self._format_recommendations_markdown(analysis.get('recommendations', []))}

## Test Results

| Test Name | Suite | Status | Metrics |
|-----------|-------|--------|---------|
{self._format_test_results_markdown(results.get('test_cases', []))}
"""
        with open(output, 'w') as f:
            f.write(md)

        return output

    def _format_bottlenecks_markdown(self, bottlenecks: list) -> str:
        """Format bottlenecks for Markdown."""
        if not bottlenecks:
            return "✅ No bottlenecks detected"

        return "\n".join(f"- **{b.get('type', 'unknown')}:** {b.get('description', '')}"
                        for b in bottlenecks)

    def _format_recommendations_markdown(self, recommendations: list) -> str:
        """Format recommendations for Markdown."""
        if not recommendations:
            return "No specific recommendations"

        md = ""
        for rec in recommendations:
            md += f"### [{rec.get('priority', 'normal').upper()}] {rec.get('category', '').title()}\n\n"
            md += f"{rec.get('description', '')}\n\n"
            if rec.get('commands'):
                md += "```bash\n" + "\n".join(rec['commands']) + "\n```\n\n"

        return md

    def _format_test_results_markdown(self, test_cases: list) -> str:
        """Format test results for Markdown table."""
        rows = []
        for tc in test_cases:
            metrics_str = ", ".join(f"{k}: {v}" for k, v in tc.get('metrics', {}).items())
            rows.append(
                f"| {tc.get('name', 'Unknown')} | {tc.get('suite', 'Unknown')} | "
                f"{tc.get('status', 'unknown').upper()} | {metrics_str or 'N/A'} |"
            )
        return "\n".join(rows)

    def _generate_json(
        self,
        analysis: Dict[str, Any],
        test_plan: Dict[str, Any],
        results: Dict[str, Any],
        output: str
    ) -> str:
        """Generate JSON report."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "test_plan": test_plan,
            "results": results,
            "analysis": analysis
        }

        with open(output, 'w') as f:
            json.dump(report, f, indent=2)

        return output
