"""
Flask web application for the dashboard.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from flask import Flask, render_template, jsonify, request, send_from_directory
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


def create_app(data_dir: str = "./test_results") -> Optional[Any]:
    """
    Create Flask application.

    Args:
        data_dir: Directory containing test results

    Returns:
        Flask app instance or None if Flask not available
    """
    if not FLASK_AVAILABLE:
        print("Flask not installed. Run: pip install flask")
        return None

    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    app.config['DATA_DIR'] = Path(data_dir)
    app.config['DATA_DIR'].mkdir(parents=True, exist_ok=True)

    @app.route('/')
    def index():
        """Main dashboard page."""
        return render_template('dashboard.html')

    @app.route('/api/tests')
    def get_tests():
        """Get list of all test runs."""
        tests = []
        data_dir = app.config['DATA_DIR']

        for result_file in data_dir.glob('*.json'):
            try:
                with open(result_file) as f:
                    data = json.load(f)
                    tests.append({
                        'id': result_file.stem,
                        'timestamp': data.get('timestamp', ''),
                        'status': data.get('status', 'unknown'),
                        'verdict': data.get('verdict', 'N/A'),
                        'score': data.get('score', 0)
                    })
            except Exception as e:
                print(f"Error loading {result_file}: {e}")
                continue

        # Sort by timestamp descending
        tests.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return jsonify(tests)

    @app.route('/api/test/<test_id>')
    def get_test_details(test_id):
        """Get detailed test results."""
        result_file = app.config['DATA_DIR'] / f"{test_id}.json"

        if not result_file.exists():
            return jsonify({'error': 'Test not found'}), 404

        try:
            with open(result_file) as f:
                return jsonify(json.load(f))
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/metrics/latest')
    def get_latest_metrics():
        """Get latest test metrics."""
        data_dir = app.config['DATA_DIR']
        result_files = sorted(data_dir.glob('*.json'),
                            key=lambda x: x.stat().st_mtime,
                            reverse=True)

        if not result_files:
            return jsonify({'error': 'No test results found'}), 404

        try:
            with open(result_files[0]) as f:
                data = json.load(f)
                return jsonify({
                    'metrics': data.get('metrics', {}),
                    'timestamp': data.get('timestamp', ''),
                    'test_id': result_files[0].stem
                })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/metrics/history')
    def get_metrics_history():
        """Get historical metrics data."""
        metric_name = request.args.get('metric', 'max_latency')
        limit = int(request.args.get('limit', 50))

        history = []
        data_dir = app.config['DATA_DIR']
        result_files = sorted(data_dir.glob('*.json'),
                            key=lambda x: x.stat().st_mtime)

        for result_file in result_files[-limit:]:
            try:
                with open(result_file) as f:
                    data = json.load(f)
                    metrics = data.get('metrics', {})

                    if metric_name in metrics:
                        history.append({
                            'timestamp': data.get('timestamp', ''),
                            'value': metrics[metric_name],
                            'test_id': result_file.stem
                        })
            except Exception as e:
                continue

        return jsonify(history)

    @app.route('/api/status')
    def get_status():
        """Get dashboard status."""
        data_dir = app.config['DATA_DIR']
        result_files = list(data_dir.glob('*.json'))

        return jsonify({
            'status': 'running',
            'total_tests': len(result_files),
            'last_updated': datetime.now().isoformat()
        })

    @app.route('/api/trends')
    def get_trends():
        """Get performance trends."""
        days = int(request.args.get('days', 7))

        trends = {
            'latency': [],
            'throughput': [],
            'errors': []
        }

        data_dir = app.config['DATA_DIR']
        result_files = sorted(data_dir.glob('*.json'),
                            key=lambda x: x.stat().st_mtime)

        for result_file in result_files[-days*24:]:  # Approximate hourly tests
            try:
                with open(result_file) as f:
                    data = json.load(f)
                    metrics = data.get('metrics', {})
                    timestamp = data.get('timestamp', '')

                    if 'max_latency' in metrics:
                        trends['latency'].append({
                            'timestamp': timestamp,
                            'value': metrics['max_latency']
                        })

                    if 'throughput' in metrics:
                        trends['throughput'].append({
                            'timestamp': timestamp,
                            'value': metrics['throughput']
                        })

                    if 'errors' in metrics:
                        trends['errors'].append({
                            'timestamp': timestamp,
                            'value': metrics['errors']
                        })
            except Exception as e:
                continue

        return jsonify(trends)

    @app.route('/api/comparison')
    def get_comparison():
        """Compare recent tests."""
        limit = int(request.args.get('limit', 10))

        comparisons = []
        data_dir = app.config['DATA_DIR']
        result_files = sorted(data_dir.glob('*.json'),
                            key=lambda x: x.stat().st_mtime,
                            reverse=True)[:limit]

        for result_file in result_files:
            try:
                with open(result_file) as f:
                    data = json.load(f)
                    comparisons.append({
                        'test_id': result_file.stem,
                        'timestamp': data.get('timestamp', ''),
                        'verdict': data.get('verdict', 'N/A'),
                        'score': data.get('score', 0),
                        'metrics': data.get('metrics', {})
                    })
            except Exception as e:
                continue

        return jsonify(comparisons)

    return app
