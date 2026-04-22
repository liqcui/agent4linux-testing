# Agent4Linux-Testing

An intelligent AI agent for Linux testing automation - designs test cases, executes tests, and analyzes results.

## Overview

Agent4Linux-Testing is an AI-powered testing assistant that helps you:

- **Design Test Cases**: Automatically generate test cases based on system requirements
- **Execute Tests**: Run comprehensive Linux system tests
- **Analyze Results**: Provide intelligent analysis and optimization recommendations
- **Generate Reports**: Create detailed performance reports with visualizations

## Features

### Core Features (Phase 1 & 2)
- 🤖 **AI-Powered Test Design**: Uses LLM to understand requirements and create test plans
- 📊 **Intelligent Analysis**: Analyzes test results and identifies performance bottlenecks
- 🎯 **Automated Testing**: Integrates with linux-testing suite for comprehensive coverage
- 📈 **Performance Insights**: Provides actionable optimization recommendations
- 🔄 **Continuous Learning**: Improves test strategies based on historical data
- 📉 **Advanced Metrics**: Collects and analyzes detailed metrics with percentile calculations
- 📊 **Rich Visualizations**: Creates charts, graphs, and dashboards for metrics
- 🔍 **Regression Detection**: Automatically compares with baselines and detects regressions
- 🧩 **Multi-Parser Support**: Specialized parsers for 6+ test suite types (rt-tests, stress-ng, iperf3, fio, STREAM, UnixBench, etc.)

### Production Features (Phase 3)
- 🌐 **Web Dashboard**: Real-time monitoring with responsive UI and auto-refresh
- 📊 **Interactive Charts**: Latency trends, throughput analysis, time-series data
- 🗄️ **Historical Tracking**: SQLite-based persistent storage with trend analysis
- 📈 **Anomaly Detection**: Statistical anomaly detection using z-scores
- 🔄 **CI/CD Integration**: Auto-generated pipelines for GitHub Actions, Jenkins, GitLab CI
- 🎯 **Baseline Management**: Create, compare, and manage performance baselines
- 📧 **Automated Alerts**: Email notifications on performance regressions
- 📦 **Export Capabilities**: JSON export for historical data analysis

### Enterprise Features (Phase 4) ⭐ NEW
- 🌍 **Distributed Testing**: Multi-system test coordination with worker pools
- 🤖 **ML Anomaly Detection**: Isolation Forest, statistical, and time-series analysis
- 📊 **Performance Prediction**: Trend forecasting and capacity planning
- 🚨 **Advanced Alerting**: Slack, PagerDuty, Email channels with rule engine
- 📈 **Prometheus Integration**: Metrics exporter with HTTP endpoint
- 📊 **Grafana Dashboards**: Auto-generated dashboards and alert rules
- ⚖️ **Intelligent Scheduling**: Priority-based test distribution
- 🔄 **Auto-scaling**: Dynamic worker pool management

## Architecture

```
agent4linux-testing/
├── agent/                  # AI agent core
│   ├── planner.py         # Test case design and planning
│   ├── executor.py        # Test execution engine
│   ├── analyzer.py        # Result analysis
│   └── reporter.py        # Report generation
├── models/                # LLM integration
│   ├── llm_client.py      # LLM API client
│   └── prompts.py         # Prompt templates
├── integrations/          # External tool integrations
│   ├── linux_testing.py   # linux-testing suite integration
│   └── metrics.py         # Metrics collection
├── utils/                 # Utilities
│   ├── parser.py          # Result parsing
│   └── visualizer.py      # Visualization tools
├── tests/                 # Unit tests
├── examples/              # Usage examples
└── docs/                  # Documentation
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/liqcui/agent4linux-testing.git
cd agent4linux-testing

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Usage

```python
from agent import TestingAgent

# Initialize the agent
agent = TestingAgent(
    llm_provider="openai",  # or "anthropic", "local"
    model="gpt-4"
)

# Design test cases
test_plan = agent.design_test_cases(
    requirement="Test memory performance under high load",
    system_info=agent.get_system_info()
)

# Execute tests
results = agent.execute_tests(test_plan)

# Analyze results
analysis = agent.analyze_results(results)

# Generate report
agent.generate_report(analysis, output="report.html")
```

### Command Line Interface

```bash
# Design and execute tests
python -m agent4linux design \
    --requirement "Evaluate network latency under stress" \
    --output test_plan.json

# Execute test plan
python -m agent4linux execute \
    --plan test_plan.json \
    --output results.json

# Analyze results
python -m agent4linux analyze \
    --results results.json \
    --output analysis.json

# Generate report
python -m agent4linux report \
    --analysis analysis.json \
    --format html \
    --output report.html
```

## Use Cases

### 1. Performance Testing

```python
# Automatic performance benchmark
agent.performance_benchmark(
    subsystems=["cpu", "memory", "network", "io"],
    duration="1h",
    workload="production"
)
```

### 2. Regression Testing

```python
# Compare with baseline
agent.regression_test(
    baseline="baseline_results.json",
    threshold=0.05  # 5% performance degradation
)
```

### 3. Custom Test Design

```python
# Design custom test scenario
agent.design_custom_test(
    scenario="""
    Test real-time performance of the system under:
    1. CPU stress (80% load)
    2. Network traffic (1Gbps)
    3. I/O operations (10K IOPS)

    Requirements:
    - Max latency < 100μs
    - P99 latency < 50μs
    - Zero packet loss
    """
)
```

## Integration with linux-testing

This agent integrates seamlessly with the [linux-testing](https://github.com/liqcui/linux-testing) suite:

```python
# Reference the linux-testing repository
agent.set_testing_suite("/path/to/linux-testing")

# Use existing test suites
agent.use_test_suite("stress-ng")
agent.use_test_suite("rt-tests")
agent.use_test_suite("fio")
```

## Supported Test Categories

The agent can design and analyze tests for:

- ✅ **Real-time Performance** (rt-tests, cyclictest)
- ✅ **System Stress** (stress-ng specialized tests)
- ✅ **Network Performance** (iperf3, netperf, qperf)
- ✅ **Disk I/O** (fio, iozone)
- ✅ **Memory Performance** (STREAM, memtester)
- ✅ **eBPF Tracing** (bcc, bpftrace)
- ✅ **System Benchmarks** (UnixBench, lmbench)
- ✅ **Functionality** (LTP, cgroup, namespace)

## AI Capabilities

### Test Design

The AI agent can:
- Understand natural language requirements
- Map requirements to appropriate test suites
- Generate test parameters based on system capabilities
- Create test execution plans with dependencies
- Optimize test sequences for efficiency

### Result Analysis

The AI agent provides:
- Performance bottleneck identification
- Statistical analysis (percentiles, distributions)
- Anomaly detection
- Comparison with industry benchmarks
- Root cause analysis for failures

### Optimization Recommendations

The agent suggests:
- Kernel parameter tuning
- System configuration changes
- Hardware upgrade recommendations
- Workload optimization strategies
- Performance best practices

## Example Workflow

```python
from agent import TestingAgent

# Initialize agent
agent = TestingAgent()

# Natural language requirement
requirement = """
I need to validate my server can handle:
- 10,000 concurrent TCP connections
- 1GB/s network throughput
- Max latency under 10ms
- Zero packet loss

Please design comprehensive tests.
"""

# Agent designs test plan
plan = agent.design(requirement)
print(f"Test plan: {plan.summary()}")
# Output:
# Test Plan:
# 1. Network baseline (iperf3) - 5 min
# 2. TCP connection stress (stress-ng sock) - 10 min
# 3. Latency measurement (qperf) - 5 min
# 4. Combined stress test - 15 min

# Execute tests
results = agent.execute(plan)

# Analyze results
analysis = agent.analyze(results)
print(analysis.verdict)
# Output: PASS - All requirements met
# Details:
# - Max connections: 12,500 ✓
# - Throughput: 1.2 GB/s ✓
# - P99 latency: 8.3 ms ✓
# - Packet loss: 0% ✓

# Get recommendations
recommendations = analysis.recommendations
for rec in recommendations:
    print(f"💡 {rec.category}: {rec.description}")
# Output:
# 💡 Optimization: Increase net.core.somaxconn to 65535
# 💡 Monitoring: Set up alerts for latency > 5ms
```

## Configuration

Create `config.yaml`:

```yaml
# LLM Configuration
llm:
  provider: openai  # openai, anthropic, local
  model: gpt-4
  api_key: ${OPENAI_API_KEY}
  temperature: 0.1

# Testing Suite Integration
linux_testing:
  path: /path/to/linux-testing
  auto_discover: true

# Analysis Settings
analysis:
  baseline_comparison: true
  statistical_analysis: true
  anomaly_detection: true
  percentiles: [50, 90, 95, 99, 99.9]

# Report Settings
report:
  format: html  # html, pdf, markdown, json
  include_graphs: true
  include_raw_data: false
  template: default
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run linter
flake8 agent/

# Format code
black agent/
```

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Roadmap

- [x] **Phase 1: Core agent implementation**
  - [x] Project structure
  - [x] LLM integration
  - [x] Test planner
  - [x] Test executor
  - [x] Result analyzer
  - [x] Report generator

- [x] **Phase 2: Advanced features** ✅ **COMPLETED**
  - [x] Multi-LLM support (OpenAI, Anthropic, local models)
  - [x] Advanced test suite parsers (6 specialized parsers)
  - [x] Enhanced metrics collection and aggregation
  - [x] Statistical analysis with percentiles (P50, P90, P95, P99, P99.9)
  - [x] Baseline comparison and regression detection
  - [x] Metrics visualization (charts, graphs, dashboards)
  - [x] Full LLM API integration (OpenAI & Anthropic)

  **See [PHASE2_FEATURES.md](PHASE2_FEATURES.md) for detailed documentation.**

- [x] **Phase 3: Production features** ✅ **COMPLETED**
  - [x] Web dashboard (Flask-based with Chart.js)
  - [x] Real-time monitoring and visualization
  - [x] Historical tracking with SQLite database
  - [x] Trend analysis and anomaly detection
  - [x] Baseline management
  - [x] CI/CD integration (GitHub Actions, Jenkins, GitLab CI)
  - [x] Auto-generated pipeline configurations
  - [x] Performance summary and reporting

  **See [PHASE3_FEATURES.md](PHASE3_FEATURES.md) for detailed documentation.**

- [x] **Phase 4: Enterprise features** ✅ **COMPLETED**
  - [x] Multi-system distributed testing with coordinator/worker architecture
  - [x] Intelligent test scheduling with priority queues
  - [x] Machine learning-based anomaly detection (Isolation Forest, Statistical, Time-Series)
  - [x] Performance prediction and trend forecasting
  - [x] Advanced alerting (Slack, PagerDuty, Email, Webhooks)
  - [x] Alert rules engine with conditions and cooldowns
  - [x] Prometheus metrics exporter with HTTP endpoint
  - [x] Grafana dashboard auto-generation
  - [x] Production-ready architecture with Docker/Kubernetes support

  **See [PHASE4_FEATURES.md](PHASE4_FEATURES.md) for detailed documentation.**

---

**🎉 All development phases complete! Production-ready enterprise testing framework.**

## License

MIT License - see [LICENSE](LICENSE) file

## Acknowledgments

- Built on top of [linux-testing](https://github.com/liqcui/linux-testing) suite
- Inspired by AI-powered testing frameworks
- Uses industry-standard benchmarking tools

## Contact

- Author: liqcui
- GitHub: [@liqcui](https://github.com/liqcui)
- Issues: [GitHub Issues](https://github.com/liqcui/agent4linux-testing/issues)

---

**Status:** 🚧 Under Development
**Version:** 0.1.0
**Last Updated:** 2026-04-22
