### Quick Start Guide - Agent4Linux-Testing

## 5-Minute Setup

### 1. Install Dependencies

```bash
cd /Users/liqcui/goproject/github.com/liqcui/agent4linux-testing

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set API Key

```bash
# For OpenAI
export OPENAI_API_KEY="your-api-key-here"

# Or for Anthropic
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 3. Run Your First Test

```bash
# Method 1: Using Python API
python examples/basic_usage.py

# Method 2: Using CLI
python -m agent4linux run --requirement "Test my server's CPU and memory performance"
```

## Common Use Cases

### Case 1: Performance Benchmark

```python
from agent import TestingAgent

agent = TestingAgent()
results = agent.performance_benchmark(
    subsystems=["cpu", "memory", "network", "io"],
    duration="30m"
)
```

### Case 2: Real-time Testing

```bash
python -m agent4linux run --requirement \
  "Test real-time latency under stress. Requirements: Max < 100μs, P99 < 50μs"
```

### Case 3: Custom Test

```python
from agent import TestingAgent

agent = TestingAgent()

requirement = """
Test web server capacity:
- 10,000 concurrent connections
- 1 GB/s throughput
- < 10ms response time
"""

workflow = agent.run_full_workflow(requirement)
print(f"Verdict: {workflow['analysis']['verdict']}")
```

## Project Structure

```
agent4linux-testing/
├── agent/              # Core agent components
│   ├── agent.py       # Main orchestrator
│   ├── planner.py     # Test designer (AI)
│   ├── executor.py    # Test runner
│   ├── analyzer.py    # Result analyzer (AI)
│   └── reporter.py    # Report generator
├── models/            # LLM integration
├── examples/          # Usage examples
└── __main__.py        # CLI entry point
```

## Key Features

1. **Natural Language Input**: Describe what you want to test in plain English
2. **Automated Design**: AI creates comprehensive test plans
3. **Multi-Suite Integration**: Uses 34 test suites from linux-testing
4. **Intelligent Analysis**: AI identifies bottlenecks and suggests optimizations
5. **Beautiful Reports**: HTML, Markdown, or JSON output

## Next Steps

1. Review the main README.md
2. Try the examples/basic_usage.py
3. Customize for your specific needs
4. Check out the linux-testing suite integration

## Troubleshooting

**No API Key?**
- The agent will work with limited functionality
- Fallback to basic test plans without AI insights

**Can't find linux-testing?**
- Agent auto-detects common locations
- Or set manually: `agent.executor.linux_testing_path = "/path/to/linux-testing"`

**Tests failing?**
- Use `dry_run=True` to simulate execution
- Check system requirements for test suites
- Ensure sudo access for privileged tests
