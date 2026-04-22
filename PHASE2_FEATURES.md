# Phase 2 Features Documentation

## Overview

Phase 2 introduces advanced metrics collection, parsing, visualization, and full LLM integration to the Agent4Linux-Testing framework.

## New Features

### 1. Advanced Test Suite Parsers

Located in `integrations/parsers.py`, these parsers extract detailed metrics from various test tool outputs:

#### RTTestsParser
Parses output from rt-tests suite (cyclictest, etc.)

**Extracted Metrics:**
- Per-thread latency statistics (min, avg, max)
- Thread priority and configuration
- Overall statistics (max, avg, std dev)
- SMI count

**Example:**
```python
from integrations import RTTestsParser

parser = RTTestsParser()
metrics = parser.parse(cyclictest_output)

print(f"Overall Max Latency: {metrics['statistics']['overall_max']} us")
print(f"Thread Count: {metrics['statistics']['thread_count']}")
```

#### StressNGParser
Parses stress-ng benchmark output

**Extracted Metrics:**
- Bogo operations per second
- Real/user/system time
- Throughput (GB/sec, MB/sec)
- Per-stressor performance

**Example:**
```python
from integrations import StressNGParser

parser = StressNGParser()
metrics = parser.parse(stress_ng_output)

for stressor, data in metrics['stressors'].items():
    print(f"{stressor}: {data['bogo_ops_per_sec_real']:.2f} ops/s")
```

#### NetworkParser
Parses iperf3, netperf, and qperf output

**Extracted Metrics:**
- Throughput (Mbps, Gbps)
- Packet loss percentage
- Transaction rate
- Latency (microseconds)
- Bandwidth

**Example:**
```python
from integrations import NetworkParser

parser = NetworkParser()
metrics = parser.parse(iperf3_output)

print(f"TX: {metrics['throughput_tx_mbps']:.2f} Mbps")
print(f"RX: {metrics['throughput_rx_mbps']:.2f} Mbps")
```

#### IOParser
Parses fio and iozone benchmark output

**Extracted Metrics:**
- IOPS (operations per second)
- Bandwidth (MB/s)
- Latency (average, P99)
- Read/write throughput

**Example:**
```python
from integrations import IOParser

parser = IOParser()
metrics = parser.parse(fio_output)

print(f"IOPS: {metrics['iops']:.0f}")
print(f"Bandwidth: {metrics['bandwidth_mbps']:.2f} MB/s")
print(f"P99 Latency: {metrics['latency_p99_us']:.2f} us")
```

#### MemoryParser
Parses STREAM and memtester output

**Extracted Metrics:**
- Memory bandwidth (Copy, Scale, Add, Triad)
- Test pass/fail status
- Error detection

**Example:**
```python
from integrations import MemoryParser

parser = MemoryParser()
metrics = parser.parse(stream_output)

print(f"Copy: {metrics['copy_mbps']:.2f} MB/s")
print(f"Triad: {metrics['triad_mbps']:.2f} MB/s")
```

#### BenchmarkParser
Parses UnixBench and lmbench output

**Extracted Metrics:**
- System index scores
- Individual benchmark scores
- Latency measurements
- Bandwidth measurements

### 2. MetricsCollector

Located in `integrations/metrics.py`, this class provides comprehensive metrics aggregation and analysis.

#### Key Features

**Metric Collection:**
```python
from integrations import MetricsCollector

collector = MetricsCollector()

# Add metrics
collector.add_metric(
    name="max_latency",
    value=45.5,
    unit="us",
    category="real_time",
    tags={"test": "cyclictest", "run": "1"}
)
```

**Statistical Analysis:**
```python
stats = collector.get_statistics("max_latency")

print(f"Mean: {stats['mean']:.2f}")
print(f"Median: {stats['median']:.2f}")
print(f"P95: {stats['p95']:.2f}")
print(f"P99: {stats['p99']:.2f}")
print(f"P99.9: {stats['p99.9']:.2f}")
```

**Baseline Comparison:**
```python
comparison = current_metrics.compare_with_baseline(
    baseline=baseline_metrics,
    threshold=0.05  # 5% threshold
)

print(f"Regressions: {len(comparison['regressions'])}")
print(f"Improvements: {len(comparison['improvements'])}")
print(f"Stable: {len(comparison['stable'])}")
```

**Filtering:**
```python
# Filter by category
rt_metrics = collector.filter_by_category("real_time")

# Filter by tags
run1_metrics = collector.filter_by_tags({"run": "1"})
```

**Percentile Calculations:**
The collector automatically calculates:
- P50 (median)
- P90
- P95
- P99
- P99.9

### 3. MetricsVisualizer

Located in `utils/visualizer.py`, this class creates various chart types for metrics visualization.

#### Chart Types

**Line Charts:**
```python
from utils import MetricsVisualizer

visualizer = MetricsVisualizer(output_dir="./charts")

chart_path = visualizer.create_metric_chart(
    metric_name="latency",
    values=[45, 48, 52, 47, 49],
    chart_type="line",
    title="Latency Over Time",
    unit="us"
)
```

**Histograms:**
```python
chart_path = visualizer.create_metric_chart(
    metric_name="latency",
    values=latency_values,
    chart_type="histogram",
    title="Latency Distribution",
    unit="us"
)
```

**Percentile Charts:**
```python
chart_path = visualizer.create_percentile_chart(
    metric_name="latency",
    percentiles={"p50": 48, "p90": 52, "p95": 53, "p99": 55},
    unit="us"
)
```

**Comparison Charts:**
```python
chart_path = visualizer.create_comparison_chart(
    baseline={"latency": 45, "throughput": 950},
    current={"latency": 48, "throughput": 980},
    title="Baseline vs Current"
)
```

**Time Series:**
```python
chart_path = visualizer.create_time_series(
    metrics={
        "latency": [{"value": 45}, {"value": 48}, ...],
        "throughput": [{"value": 950}, {"value": 960}, ...]
    },
    title="Metric Trends"
)
```

**Regression Analysis:**
```python
chart_path = visualizer.create_regression_chart(
    regressions=[...],
    improvements=[...],
    stable=[...]
)
```

#### Fallback Mode

If matplotlib/plotly are not available, the visualizer automatically falls back to text-based charts saved as `.txt` files.

### 4. Enhanced LLM Integration

The LLM client now supports actual API calls to OpenAI and Anthropic.

#### OpenAI Integration

```python
from models import LLMClient

client = LLMClient(
    provider="openai",
    model="gpt-4",
    api_key="your-api-key"
)

response = client.generate(
    prompt="Design a test plan for...",
    temperature=0.1,
    max_tokens=2000
)
```

#### Anthropic Integration

```python
client = LLMClient(
    provider="anthropic",
    model="claude-3-opus-20240229",
    api_key="your-api-key"
)

response = client.generate(
    prompt="Analyze these test results...",
    temperature=0.1,
    max_tokens=2000
)
```

#### Fallback Mode

When API keys are not available, the client falls back to basic test planning without AI insights.

## Usage Examples

### Example 1: Complete Workflow with Metrics Collection

```python
from agent import TestingAgent
from integrations import MetricsCollector
from utils import MetricsVisualizer

# Initialize
agent = TestingAgent()
collector = MetricsCollector()
visualizer = MetricsVisualizer()

# Design and execute tests
requirement = "Test real-time latency under moderate load"
test_plan = agent.design_test_cases(requirement)
results = agent.execute_tests(test_plan)

# Collect metrics
for test in results['test_cases']:
    for metric_name, value in test['metrics'].items():
        collector.add_metric(
            name=metric_name,
            value=value,
            unit=test.get('unit', ''),
            category=test['suite']
        )

# Analyze
stats = collector.get_statistics("max_latency")
summary = collector.generate_summary()

# Visualize
chart = visualizer.create_percentile_chart(
    metric_name="max_latency",
    percentiles=stats
)

# Generate report
report = agent.generate_report(
    analysis=agent.analyze_results(results),
    output="report.html",
    format="html"
)
```

### Example 2: Regression Testing

```python
# Load baseline
baseline_collector = MetricsCollector()
baseline_collector.import_from_dict(baseline_data)

# Run current tests
current_collector = MetricsCollector()
# ... collect current metrics ...

# Compare
comparison = current_collector.compare_with_baseline(
    baseline=baseline_collector,
    threshold=0.05
)

# Visualize regressions
chart = visualizer.create_regression_chart(
    regressions=comparison['regressions'],
    improvements=comparison['improvements'],
    stable=comparison['stable']
)

# Alert on regressions
if comparison['regressions']:
    print(f"⚠️  {len(comparison['regressions'])} regressions detected!")
    for reg in comparison['regressions']:
        print(f"  - {reg['metric']}: {reg['change_percent']:+.2f}%")
```

## Integration with Existing Components

### TestExecutor Integration

The executor now uses advanced parsers automatically:

```python
# In executor.py
def _parse_metrics(self, suite: str, output: str):
    parser = self.parsers.get(suite.lower())
    if parser:
        return parser.parse(output)
    # ... fallback to basic parsing
```

### ReportGenerator Integration

The reporter now includes visualizations:

```python
# In reporter.py
def _generate_html(self, analysis, test_plan, results, output):
    # Generate charts
    charts = self.visualizer.create_metric_chart(...)
    # Embed in HTML report
```

## Configuration

### Environment Variables

```bash
# OpenAI API
export OPENAI_API_KEY="sk-..."

# Anthropic API
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Visualization Settings

```python
# Custom output directory
visualizer = MetricsVisualizer(output_dir="/path/to/charts")

# Chart customization
chart = visualizer.create_metric_chart(
    metric_name="latency",
    values=values,
    chart_type="line",  # or "bar", "histogram"
    title="Custom Title",
    unit="us"
)
```

## Performance Considerations

- **Parser Performance**: Regex-based parsing is efficient for most outputs
- **Memory Usage**: MetricsCollector stores all raw data; consider periodic exports for long-running tests
- **Visualization**: matplotlib/plotly are optional; fallback mode uses minimal resources

## Error Handling

All components include graceful fallbacks:
- Parsers fall back to basic extraction on parse errors
- MetricsCollector handles missing data gracefully
- Visualizer falls back to text charts if graphing libraries unavailable
- LLM client falls back to basic templates if API unavailable

## Testing

Run the advanced examples:

```bash
# Basic functionality
python examples/advanced_usage.py

# With API integration
export OPENAI_API_KEY="your-key"
python examples/advanced_usage.py

# Full workflow
python -m agent4linux run --requirement "Your test requirement"
```

## Next Steps (Phase 3)

- Real-time dashboard with live updates
- Historical trend analysis
- Machine learning-based anomaly detection
- Integration with CI/CD pipelines
- Distributed testing support
