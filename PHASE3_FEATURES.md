# Phase 3 Features Documentation

## Overview

Phase 3 introduces web dashboard, historical tracking, and CI/CD integration for production-ready testing automation.

## New Features

### 1. Web Dashboard

Real-time web-based dashboard for monitoring test results and performance metrics.

#### Components

- **Flask Application** (`dashboard/app.py`): REST API backend
- **Dashboard Server** (`dashboard/server.py`): Server manager with background execution
- **HTML Dashboard** (`dashboard/templates/dashboard.html`): Responsive web UI with Chart.js

####Features

**Real-time Metrics Display:**
- Total test count
- Latest test score
- Average latency
- Pass rate statistics

**Interactive Charts:**
- Latency trend visualization
- Throughput trend analysis
- Historical comparison
- Time-series data

**Test Results Table:**
- Recent test runs
- Status indicators
- Clickable test details
- Auto-refresh every 30 seconds

#### Usage

```python
from dashboard import DashboardServer

# Initialize server
server = DashboardServer(
    host="0.0.0.0",
    port=5000,
    data_dir="./test_results"
)

# Start in background
server.start(background=True)

# Server accessible at http://localhost:5000
```

**Command Line:**
```bash
python examples/phase3_usage.py --dashboard
```

#### API Endpoints

- `GET /` - Main dashboard page
- `GET /api/tests` - List all test runs
- `GET /api/test/<test_id>` - Get test details
- `GET /api/metrics/latest` - Get latest metrics
- `GET /api/metrics/history?metric=<name>&limit=<n>` - Get metric history
- `GET /api/status` - Get dashboard status
- `GET /api/trends?days=<n>` - Get performance trends
- `GET /api/comparison?limit=<n>` - Compare recent tests

#### Screenshots

The dashboard includes:
- Modern gradient header with status indicator
- Responsive grid layout for statistics cards
- Interactive line charts for trends
- Sortable test results table
- Auto-refreshing data (30s interval)

### 2. Historical Tracking

SQLite-based persistent storage for test history and trend analysis.

#### Components

- **HistoryDatabase** (`history/database.py`): SQLite database management
- **HistoryTracker** (`history/tracker.py`): High-level tracking API

#### Database Schema

**Tables:**
- `test_runs`: Test execution records
- `test_cases`: Individual test case results
- `metrics`: Performance metrics with timestamps
- `baselines`: Performance baselines

**Indexes:**
- `idx_runs_timestamp`: Fast time-based queries
- `idx_metrics_name`: Fast metric lookups
- `idx_metrics_timestamp`: Time-series queries

#### Features

**Test Run Recording:**
```python
from history import HistoryTracker

tracker = HistoryTracker(db_path="./history.db")

# Record test run
run_id = tracker.record_test_run({
    'test_id': 'test_20260422_120000',
    'timestamp': '2026-04-22T12:00:00',
    'requirement': 'Performance baseline',
    'status': 'completed',
    'verdict': 'PASS',
    'score': 85.5,
    'test_cases': [...]
})
```

**Trend Analysis:**
```python
# Analyze metric trend
trend = tracker.get_metric_trend('max_latency', days=7)

print(f"Trend: {trend['trend']}")  # increasing/decreasing/stable
print(f"Change: {trend['change_percent']:.2f}%")
print(f"Current avg: {trend['current_avg']:.2f}")
```

**Baseline Comparison:**
```python
# Create baseline
baseline_id = tracker.create_baseline_from_run(
    test_id='test_20260422_120000',
    baseline_name='baseline-main',
    description='Main branch baseline'
)

# Compare with baseline
comparison = tracker.compare_with_baseline(
    test_id='test_20260422_130000',
    baseline_name='baseline-main'
)

print(f"Regressions: {len(comparison['regressions'])}")
print(f"Improvements: {len(comparison['improvements'])}")
```

**Performance Summary:**
```python
# Get 30-day summary
summary = tracker.get_performance_summary(days=30)

print(f"Total runs: {summary['total_runs']}")
print(f"Pass rate: {summary['pass_rate']:.1f}%")
print(f"Avg score: {summary['avg_score']:.1f}")
```

**Anomaly Detection:**
```python
# Detect anomalies using standard deviation
anomalies = tracker.detect_anomalies('max_latency', threshold=2.0)

for anomaly in anomalies:
    print(f"Anomaly at {anomaly['timestamp']}")
    print(f"  Value: {anomaly['value']}")
    print(f"  Z-score: {anomaly['z_score']:.2f}")
```

**Data Export:**
```python
# Export to JSON
tracker.export_to_json('export.json', days=30)
```

### 3. CI/CD Integration

Auto-generated configuration files for popular CI/CD platforms.

#### Supported Platforms

1. **GitHub Actions** (`cicd/github_actions.py`)
2. **Jenkins** (`cicd/jenkins.py`)
3. **GitLab CI** (`cicd/gitlab_ci.py`)

#### GitHub Actions

**Generate Workflow:**
```python
from cicd import GitHubActionsIntegration

# Generate performance test workflow
GitHubActionsIntegration.generate_workflow(
    name="Linux Performance Testing",
    schedule="0 0 * * *",  # Daily at midnight
    output_path=".github/workflows/performance-test.yml"
)

# Generate baseline creation workflow
GitHubActionsIntegration.generate_baseline_workflow(
    output_path=".github/workflows/create-baseline.yml"
)
```

**Features:**
- Runs on push, PR, and schedule
- Installs test tools (stress-ng, iperf3, fio)
- Executes performance tests
- Compares with baseline
- Posts results as PR comment
- Fails on regressions
- Uploads test artifacts

**Required Secrets:**
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`

#### Jenkins

**Generate Jenkinsfile:**
```python
from cicd import JenkinsIntegration

# Generate main pipeline
JenkinsIntegration.generate_jenkinsfile(
    cron_schedule="H 0 * * *",
    output_path="Jenkinsfile"
)

# Generate baseline job
JenkinsIntegration.generate_baseline_job(
    output_path="Jenkinsfile.baseline"
)
```

**Features:**
- Cron-triggered execution
- Multi-stage pipeline (Setup, Test, Analyze, Report)
- HTML report publishing
- Metrics plotting
- Email notifications on regressions
- Artifact archiving
- Baseline creation job

**Required Credentials:**
- `openai-api-key` (Jenkins credential)

#### GitLab CI

**Generate Configuration:**
```python
from cicd import GitLabCIIntegration

GitLabCIIntegration.generate_gitlab_ci(
    output_path=".gitlab-ci.yml"
)
```

**Features:**
- Multi-stage pipeline (setup, test, analyze, report)
- Caching for dependencies
- Artifact management
- MR comment posting
- Regression checking
- Scheduled baseline creation
- Environment variables for metrics

**Required Variables:**
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
- `GITLAB_TOKEN` (for MR comments)

### 4. Integration Examples

#### Complete CI/CD Workflow

1. **Developer pushes code** → Triggers CI/CD pipeline
2. **CI runs performance tests** → Executes test suite
3. **Results compared with baseline** → Detects regressions
4. **Report posted to PR/MR** → Shows performance impact
5. **Pipeline fails on regressions** → Prevents merge
6. **Historical data recorded** → Tracks trends over time
7. **Dashboard updated** → Shows latest results

#### Monitoring Workflow

1. **Tests run periodically** → Scheduled execution
2. **Results stored in database** → Historical tracking
3. **Dashboard displays metrics** → Real-time visualization
4. **Trends analyzed** → Anomaly detection
5. **Alerts on regressions** → Email/Slack notifications

## Usage Examples

### Example 1: Start Dashboard

```python
from dashboard import DashboardServer

server = DashboardServer(
    host="0.0.0.0",
    port=5000,
    data_dir="./test_results"
)

# Start in background
server.start(background=True)

# Keep main program running
while True:
    time.sleep(60)
```

### Example 2: Historical Analysis

```python
from history import HistoryTracker
from agent import TestingAgent

# Run test
agent = TestingAgent()
results = agent.run_full_workflow("Test system performance")

# Record to history
tracker = HistoryTracker()
tracker.record_test_run(results)

# Analyze trends
latency_trend = tracker.get_metric_trend('max_latency', days=7)
if latency_trend['trend'] == 'increasing':
    print("⚠️ Latency is trending up!")

# Check for anomalies
anomalies = tracker.detect_anomalies('max_latency')
if anomalies:
    print(f"⚠️ {len(anomalies)} anomalies detected!")
```

### Example 3: CI/CD Setup

```python
from cicd import GitHubActionsIntegration

# Generate all CI/CD files
GitHubActionsIntegration.generate_workflow()
GitHubActionsIntegration.generate_baseline_workflow()

# Commit and push
# git add .github/workflows/
# git commit -m "Add performance testing workflow"
# git push
```

### Example 4: Production Monitoring

```python
from dashboard import DashboardServer
from history import HistoryTracker
from agent import TestingAgent
import schedule
import time

# Start dashboard
dashboard = DashboardServer(port=5000)
dashboard.start(background=True)

# Initialize tracker
tracker = HistoryTracker()

# Initialize agent
agent = TestingAgent()

def run_performance_test():
    """Run test and record results."""
    print("Running scheduled performance test...")

    results = agent.run_full_workflow(
        "Automated performance monitoring"
    )

    # Record to history
    tracker.record_test_run(results)

    # Check for regressions
    comparison = tracker.compare_with_baseline(
        results['test_id'],
        'baseline-production'
    )

    if comparison.get('regressions'):
        send_alert(comparison)

# Schedule tests
schedule.every().hour.do(run_performance_test)

# Run forever
while True:
    schedule.run_pending()
    time.sleep(60)
```

## Configuration

### Dashboard Configuration

```python
# dashboard_config.py
DASHBOARD_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'data_dir': './test_results',
    'auto_refresh_interval': 30,  # seconds
    'max_history_points': 100
}
```

### History Configuration

```python
# history_config.py
HISTORY_CONFIG = {
    'db_path': './history.db',
    'retention_days': 90,  # Auto-cleanup old data
    'anomaly_threshold': 2.0,  # Z-score
    'trend_window_days': 7
}
```

### CI/CD Configuration

```yaml
# ci_config.yml
ci:
  schedule: "0 0 * * *"  # Daily
  baseline_name: "baseline-main"
  regression_threshold: 5  # percent
  notifications:
    email: true
    slack: true
  artifacts:
    retention_days: 30
```

## Deployment

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    stress-ng iperf3 fio git

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Expose dashboard port
EXPOSE 5000

# Run dashboard
CMD ["python", "examples/phase3_usage.py", "--dashboard"]
```

```bash
# Build and run
docker build -t agent4linux-dashboard .
docker run -p 5000:5000 -v ./test_results:/app/test_results agent4linux-dashboard
```

### Kubernetes Deployment

```yaml
# k8s/deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent4linux-dashboard
spec:
  replicas: 1
  selector:
    matchLabels:
      app: agent4linux
  template:
    metadata:
      labels:
        app: agent4linux
    spec:
      containers:
      - name: dashboard
        image: agent4linux-dashboard:latest
        ports:
        - containerPort: 5000
        volumeMounts:
        - name: test-results
          mountPath: /app/test_results
      volumes:
      - name: test-results
        persistentVolumeClaim:
          claimName: test-results-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: agent4linux-service
spec:
  selector:
    app: agent4linux
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

## Best Practices

### 1. Historical Data Management

- Archive old test results after 90 days
- Create monthly baselines
- Export data periodically for backup
- Monitor database size

### 2. Dashboard Performance

- Limit history queries to last 100 points
- Use caching for expensive queries
- Enable gzip compression
- Use CDN for static assets

### 3. CI/CD Integration

- Store baselines in version control
- Use separate credentials for CI
- Enable notifications for regressions
- Archive test artifacts

### 4. Monitoring

- Set up alerts for anomalies
- Monitor test execution time
- Track pass/fail rates
- Review trends weekly

## Troubleshooting

### Dashboard Not Loading

```bash
# Check if Flask is installed
pip install flask

# Check if port is available
lsof -i :5000

# Start with debug mode
python examples/phase3_usage.py --dashboard
```

### Database Errors

```python
# Reset database
import os
os.remove('history.db')

# Reinitialize
from history import HistoryTracker
tracker = HistoryTracker()
```

### CI/CD Pipeline Failures

1. Check API key configuration
2. Verify test tools are installed
3. Check baseline file exists
4. Review pipeline logs

## Next Steps (Phase 4)

- Multi-system distributed testing
- Machine learning-based anomaly detection
- Advanced alerting and notifications
- Custom dashboard widgets
- API authentication and RBAC
- Real-time collaboration features
