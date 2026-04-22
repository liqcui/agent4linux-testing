"""
GitHub Actions integration.
"""

from pathlib import Path
from typing import Dict, Any


class GitHubActionsIntegration:
    """
    Generates GitHub Actions workflow files.
    """

    @staticmethod
    def generate_workflow(
        name: str = "Linux Performance Testing",
        schedule: str = "0 0 * * *",  # Daily at midnight
        output_path: str = ".github/workflows/performance-test.yml"
    ) -> str:
        """
        Generate GitHub Actions workflow file.

        Args:
            name: Workflow name
            schedule: Cron schedule
            output_path: Output file path

        Returns:
            Path to generated workflow file
        """
        workflow_content = f"""name: {name}

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '{schedule}'
  workflow_dispatch:

jobs:
  performance-test:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Install test tools
      run: |
        sudo apt-get update
        sudo apt-get install -y stress-ng iperf3 fio

    - name: Run performance tests
      env:
        OPENAI_API_KEY: ${{{{ secrets.OPENAI_API_KEY }}}}
      run: |
        python -m agent4linux run \\
          --requirement "Test baseline system performance" \\
          --output-dir ./test-results

    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: test-results/

    - name: Check for regressions
      run: |
        python -m agent4linux analyze \\
          --results ./test-results/results.json \\
          --baseline ./baseline/baseline.json \\
          --output ./test-results/analysis.json

    - name: Comment on PR
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v7
      with:
        script: |
          const fs = require('fs');
          const analysis = JSON.parse(fs.readFileSync('./test-results/analysis.json', 'utf8'));

          const comment = `## Performance Test Results

**Verdict:** ${{analysis.verdict}}
**Score:** ${{analysis.score}}/100

### Regressions
${{analysis.regressions.length > 0 ? analysis.regressions.map(r =>
  `- ${{r.metric}}: ${{r.change_percent.toFixed(2)}}% worse`
).join('\\n') : 'None detected ✅'}}

### Improvements
${{analysis.improvements.length > 0 ? analysis.improvements.map(i =>
  `- ${{i.metric}}: ${{Math.abs(i.change_percent).toFixed(2)}}% better`
).join('\\n') : 'None'}}
          `;

          github.rest.issues.createComment({{
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          }});

    - name: Fail on regressions
      run: |
        python -c "
import json
with open('./test-results/analysis.json') as f:
    analysis = json.load(f)
if analysis.get('regressions', []):
    print(f'❌ {{len(analysis[\\\"regressions\\\"])}} regressions detected!')
    exit(1)
print('✅ No regressions detected')
        "
"""

        # Create output directory
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write workflow file
        with open(output_file, 'w') as f:
            f.write(workflow_content)

        return str(output_file)

    @staticmethod
    def generate_baseline_workflow(
        output_path: str = ".github/workflows/create-baseline.yml"
    ) -> str:
        """
        Generate workflow to create performance baselines.

        Args:
            output_path: Output file path

        Returns:
            Path to generated workflow file
        """
        workflow_content = """name: Create Performance Baseline

on:
  workflow_dispatch:
    inputs:
      baseline_name:
        description: 'Baseline name'
        required: true
        default: 'baseline-main'

jobs:
  create-baseline:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Install test tools
      run: |
        sudo apt-get update
        sudo apt-get install -y stress-ng iperf3 fio

    - name: Run baseline tests
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        python -m agent4linux run \\
          --requirement "Complete system performance baseline" \\
          --output-dir ./baseline

    - name: Commit baseline
      run: |
        git config user.name "GitHub Actions"
        git config user.email "actions@github.com"
        mkdir -p baseline
        cp ./baseline/results.json ./baseline/${{ github.event.inputs.baseline_name }}.json
        git add baseline/
        git commit -m "Add performance baseline: ${{ github.event.inputs.baseline_name }}"
        git push
"""

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            f.write(workflow_content)

        return str(output_file)
