"""
Jenkins integration.
"""

from pathlib import Path
from typing import Dict, Any


class JenkinsIntegration:
    """
    Generates Jenkins pipeline files.
    """

    @staticmethod
    def generate_jenkinsfile(
        cron_schedule: str = "H 0 * * *",  # Daily
        output_path: str = "Jenkinsfile"
    ) -> str:
        """
        Generate Jenkinsfile for performance testing.

        Args:
            cron_schedule: Cron schedule
            output_path: Output file path

        Returns:
            Path to generated Jenkinsfile
        """
        jenkinsfile_content = f"""pipeline {{
    agent {{
        label 'linux'
    }}

    triggers {{
        cron('{cron_schedule}')
    }}

    environment {{
        OPENAI_API_KEY = credentials('openai-api-key')
        RESULTS_DIR = 'test-results'
    }}

    stages {{
        stage('Setup') {{
            steps {{
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                '''
            }}
        }}

        stage('Install Test Tools') {{
            steps {{
                sh '''
                    sudo apt-get update
                    sudo apt-get install -y stress-ng iperf3 fio
                '''
            }}
        }}

        stage('Run Performance Tests') {{
            steps {{
                sh '''
                    . venv/bin/activate
                    python -m agent4linux run \\
                        --requirement "Comprehensive system performance test" \\
                        --output-dir $RESULTS_DIR
                '''
            }}
        }}

        stage('Analyze Results') {{
            steps {{
                script {{
                    if (fileExists('baseline/baseline.json')) {{
                        sh '''
                            . venv/bin/activate
                            python -m agent4linux analyze \\
                                --results $RESULTS_DIR/results.json \\
                                --baseline baseline/baseline.json \\
                                --output $RESULTS_DIR/analysis.json
                        '''
                    }} else {{
                        echo "No baseline found, skipping comparison"
                    }}
                }}
            }}
        }}

        stage('Generate Report') {{
            steps {{
                sh '''
                    . venv/bin/activate
                    python -m agent4linux report \\
                        --analysis $RESULTS_DIR/analysis.json \\
                        --format html \\
                        --output $RESULTS_DIR/report.html
                '''
            }}
        }}

        stage('Check Regressions') {{
            steps {{
                script {{
                    def analysis = readJSON file: "$RESULTS_DIR/analysis.json"
                    if (analysis.regressions && analysis.regressions.size() > 0) {{
                        echo "⚠️ ${{analysis.regressions.size()}} regressions detected!"
                        currentBuild.result = 'UNSTABLE'

                        // Send notification
                        emailext (
                            subject: "Performance Regression Detected - Build #${{env.BUILD_NUMBER}}",
                            body: """
                            <h2>Performance Test Results</h2>
                            <p><b>Verdict:</b> ${{analysis.verdict}}</p>
                            <p><b>Score:</b> ${{analysis.score}}/100</p>

                            <h3>Regressions</h3>
                            <ul>
                            ${{analysis.regressions.collect {{ r ->
                                "<li>${{r.metric}}: ${{r.change_percent.round(2)}}% worse</li>"
                            }}.join('')}}
                            </ul>

                            <p>Full report: <a href="${{env.BUILD_URL}}artifact/test-results/report.html">View Report</a></p>
                            """,
                            to: '${{env.CHANGE_AUTHOR_EMAIL}}',
                            mimeType: 'text/html'
                        )
                    }} else {{
                        echo "✅ No regressions detected"
                    }}
                }}
            }}
        }}
    }}

    post {{
        always {{
            // Archive test results
            archiveArtifacts artifacts: 'test-results/**/*', fingerprint: true

            // Publish HTML report
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'test-results',
                reportFiles: 'report.html',
                reportName: 'Performance Test Report'
            ])

            // Record metrics
            script {{
                if (fileExists('test-results/results.json')) {{
                    def results = readJSON file: 'test-results/results.json'
                    // Plot metrics
                    plot(
                        csvFileName: 'performance-metrics.csv',
                        group: 'Performance',
                        title: 'Performance Metrics',
                        style: 'line',
                        csvSeries: [[
                            file: 'test-results/metrics.csv',
                            inclusionFlag: 'INCLUDE_BY_STRING',
                            url: ''
                        ]]
                    )
                }}
            }}
        }}

        success {{
            echo '✅ Performance tests passed successfully'
        }}

        unstable {{
            echo '⚠️ Performance regressions detected'
        }}

        failure {{
            echo '❌ Performance tests failed'
        }}

        cleanup {{
            cleanWs()
        }}
    }}
}}
"""

        output_file = Path(output_path)
        with open(output_file, 'w') as f:
            f.write(jenkinsfile_content)

        return str(output_file)

    @staticmethod
    def generate_baseline_job(output_path: str = "Jenkinsfile.baseline") -> str:
        """
        Generate Jenkinsfile for creating baselines.

        Args:
            output_path: Output file path

        Returns:
            Path to generated Jenkinsfile
        """
        jenkinsfile_content = """pipeline {
    agent {
        label 'linux'
    }

    parameters {
        string(name: 'BASELINE_NAME', defaultValue: 'baseline-main', description: 'Baseline name')
        text(name: 'DESCRIPTION', defaultValue: '', description: 'Baseline description')
    }

    environment {
        OPENAI_API_KEY = credentials('openai-api-key')
    }

    stages {
        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Baseline Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    python -m agent4linux run \\
                        --requirement "Complete system performance baseline" \\
                        --output-dir ./baseline-results
                '''
            }
        }

        stage('Save Baseline') {
            steps {
                sh '''
                    mkdir -p baseline
                    cp baseline-results/results.json baseline/${BASELINE_NAME}.json
                    echo "${DESCRIPTION}" > baseline/${BASELINE_NAME}.txt
                '''
            }
        }

        stage('Commit to Repository') {
            steps {
                sh '''
                    git config user.name "Jenkins"
                    git config user.email "jenkins@example.com"
                    git add baseline/
                    git commit -m "Add performance baseline: ${BASELINE_NAME}"
                    git push origin main
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Baseline ${params.BASELINE_NAME} created successfully"
        }
    }
}
"""

        output_file = Path(output_path)
        with open(output_file, 'w') as f:
            f.write(jenkinsfile_content)

        return str(output_file)
