"""
Prompt templates for LLM interactions.
"""

TEST_DESIGN_PROMPT = """You are an expert Linux testing engineer. Design a comprehensive test plan based on the following requirement.

**Requirement:**
{requirement}

**System Information:**
{system_info}

**Available Test Suites:**
{available_suites}

**Constraints:**
{constraints}

Please design a test plan that includes:
1. List of test cases to execute
2. Test parameters for each case
3. Expected duration
4. Dependencies between tests

Return the test plan in JSON format:
{{
    "summary": "Brief description of the test plan",
    "test_cases": [
        {{
            "name": "Test case name",
            "suite": "Test suite to use",
            "parameters": {{
                "param1": "value1"
            }},
            "estimated_duration": "5 minutes",
            "dependencies": []
        }}
    ],
    "total_estimated_duration": "30 minutes",
    "execution_order": ["test1", "test2"]
}}
"""

ANALYSIS_PROMPT = """You are an expert at analyzing Linux system test results. Analyze the following test results and provide insights.

**Test Results:**
{results}

**Preliminary Analysis:**
{analysis}

**System Information:**
{system_info}

Please provide:
1. Key insights about the test results
2. Performance bottlenecks identified
3. Root cause analysis for any failures
4. Comparison with industry benchmarks
5. Specific optimization recommendations

Focus on actionable insights that can help improve system performance.
"""

OPTIMIZATION_PROMPT = """Based on the test results and analysis, suggest specific optimizations.

**Test Results Summary:**
{results_summary}

**Identified Issues:**
{issues}

**System Configuration:**
{system_config}

Provide specific, actionable recommendations including:
1. Kernel parameter tuning
2. System configuration changes
3. Hardware recommendations (if applicable)
4. Application-level optimizations
5. Monitoring and alerting suggestions

Format each recommendation with:
- Category (kernel, network, io, memory, etc.)
- Priority (high, medium, low)
- Description
- Specific commands or changes
- Expected impact
"""

RESULT_SUMMARY_PROMPT = """Summarize the test results in a clear, concise manner suitable for a technical report.

**Test Execution Results:**
{results}

**Performance Metrics:**
{metrics}

**Analysis:**
{analysis}

Create a summary that includes:
1. Executive summary (2-3 sentences)
2. Key findings
3. Performance highlights
4. Areas of concern
5. Overall recommendation (PASS/FAIL/WARNING)

Keep it professional and data-driven.
"""
