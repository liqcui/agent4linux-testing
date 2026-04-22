"""
GitLab CI/CD integration.
"""

from pathlib import Path


class GitLabCIIntegration:
    """
    Generates GitLab CI configuration files.
    """

    @staticmethod
    def generate_gitlab_ci(
        output_path: str = ".gitlab-ci.yml"
    ) -> str:
        """
        Generate GitLab CI configuration.

        Args:
            output_path: Output file path

        Returns:
            Path to generated configuration file
        """
        gitlab_ci_content = """stages:
  - setup
  - test
  - analyze
  - report

variables:
  RESULTS_DIR: "test-results"
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip
    - venv/

# Setup Python environment
setup:
  stage: setup
  image: python:3.11
  script:
    - python -m venv venv
    - source venv/bin/activate
    - pip install -r requirements.txt
  artifacts:
    paths:
      - venv/
    expire_in: 1 hour

# Run performance tests
performance_test:
  stage: test
  image: ubuntu:latest
  dependencies:
    - setup
  before_script:
    - apt-get update
    - apt-get install -y python3 python3-venv stress-ng iperf3 fio
    - source venv/bin/activate
  script:
    - python -m agent4linux run
        --requirement "Comprehensive system performance test"
        --output-dir $RESULTS_DIR
  artifacts:
    paths:
      - $RESULTS_DIR/
    expire_in: 30 days
  only:
    - main
    - merge_requests
    - schedules

# Analyze results
analyze:
  stage: analyze
  image: python:3.11
  dependencies:
    - setup
    - performance_test
  script:
    - source venv/bin/activate
    - |
      if [ -f baseline/baseline.json ]; then
        python -m agent4linux analyze \\
          --results $RESULTS_DIR/results.json \\
          --baseline baseline/baseline.json \\
          --output $RESULTS_DIR/analysis.json
      else
        echo "No baseline found, skipping comparison"
      fi
  artifacts:
    paths:
      - $RESULTS_DIR/analysis.json
    expire_in: 30 days

# Generate report
generate_report:
  stage: report
  image: python:3.11
  dependencies:
    - setup
    - analyze
  script:
    - source venv/bin/activate
    - python -m agent4linux report
        --analysis $RESULTS_DIR/analysis.json
        --format html
        --output $RESULTS_DIR/report.html
  artifacts:
    paths:
      - $RESULTS_DIR/report.html
    expire_in: 30 days
    reports:
      dotenv: $RESULTS_DIR/metrics.env

# Check for regressions
check_regressions:
  stage: report
  image: python:3.11
  dependencies:
    - analyze
  script:
    - |
      python3 << 'EOF'
      import json
      import sys

      try:
          with open('test-results/analysis.json') as f:
              analysis = json.load(f)

          regressions = analysis.get('regressions', [])

          if regressions:
              print(f"❌ {len(regressions)} performance regressions detected!")
              for r in regressions:
                  print(f"  - {r['metric']}: {r['change_percent']:.2f}% worse")
              sys.exit(1)
          else:
              print("✅ No performance regressions detected")
      except FileNotFoundError:
          print("⚠️ No analysis file found")
          sys.exit(0)
      EOF
  allow_failure: true
  only:
    - merge_requests

# Post results to merge request
post_to_mr:
  stage: report
  image: python:3.11
  dependencies:
    - analyze
  script:
    - |
      python3 << 'EOF'
      import json
      import os
      import requests

      # Read analysis
      with open('test-results/analysis.json') as f:
          analysis = json.load(f)

      # Create comment
      regressions_text = "None detected ✅"
      if analysis.get('regressions'):
          regressions_text = "\\n".join([
              f"- {r['metric']}: {r['change_percent']:.2f}% worse"
              for r in analysis['regressions']
          ])

      improvements_text = "None"
      if analysis.get('improvements'):
          improvements_text = "\\n".join([
              f"- {i['metric']}: {abs(i['change_percent']):.2f}% better"
              for i in analysis['improvements']
          ])

      comment = f"""## Performance Test Results

**Verdict:** {analysis.get('verdict', 'N/A')}
**Score:** {analysis.get('score', 0)}/100

### Regressions
{regressions_text}

### Improvements
{improvements_text}
      """

      # Post to GitLab MR
      project_id = os.environ.get('CI_PROJECT_ID')
      mr_iid = os.environ.get('CI_MERGE_REQUEST_IID')
      token = os.environ.get('GITLAB_TOKEN')

      if all([project_id, mr_iid, token]):
          url = f"https://gitlab.com/api/v4/projects/{project_id}/merge_requests/{mr_iid}/notes"
          headers = {'PRIVATE-TOKEN': token}
          data = {'body': comment}
          requests.post(url, headers=headers, data=data)
      EOF
  only:
    - merge_requests
  when: always

# Scheduled baseline creation
create_baseline:
  stage: test
  image: ubuntu:latest
  before_script:
    - apt-get update
    - apt-get install -y python3 python3-venv stress-ng iperf3 fio
    - source venv/bin/activate
  script:
    - python -m agent4linux run
        --requirement "Complete system performance baseline"
        --output-dir ./baseline-results
    - mkdir -p baseline
    - BASELINE_NAME="baseline-$(date +%Y%m%d)"
    - cp baseline-results/results.json baseline/$BASELINE_NAME.json
    - git config user.name "GitLab CI"
    - git config user.email "ci@gitlab.com"
    - git add baseline/
    - git commit -m "Add performance baseline: $BASELINE_NAME"
    - git push https://oauth2:${GITLAB_TOKEN}@gitlab.com/${CI_PROJECT_PATH}.git HEAD:main
  only:
    - schedules
  when: manual
"""

        output_file = Path(output_path)
        with open(output_file, 'w') as f:
            f.write(gitlab_ci_content)

        return str(output_file)
