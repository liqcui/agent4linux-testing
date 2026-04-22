"""
Database for storing historical test results.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class HistoryDatabase:
    """
    SQLite database for historical test data.
    """

    def __init__(self, db_path: str = "./history.db"):
        """
        Initialize database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.conn = None
        self._initialize_db()

    def _initialize_db(self):
        """Create database tables if they don't exist."""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        cursor = self.conn.cursor()

        # Test runs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                requirement TEXT,
                status TEXT,
                verdict TEXT,
                score REAL,
                duration REAL,
                metadata TEXT
            )
        """)

        # Test cases table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER,
                name TEXT NOT NULL,
                suite TEXT NOT NULL,
                status TEXT,
                start_time TEXT,
                end_time TEXT,
                output TEXT,
                FOREIGN KEY (run_id) REFERENCES test_runs(id)
            )
        """)

        # Metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER,
                case_id INTEGER,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT,
                category TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES test_runs(id),
                FOREIGN KEY (case_id) REFERENCES test_cases(id)
            )
        """)

        # Baselines table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS baselines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                run_id INTEGER,
                created_at TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY (run_id) REFERENCES test_runs(id)
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_timestamp ON test_runs(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)")

        self.conn.commit()

    def save_test_run(self, test_data: Dict[str, Any]) -> int:
        """
        Save a test run to database.

        Args:
            test_data: Test run data

        Returns:
            Run ID
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO test_runs (test_id, timestamp, requirement, status, verdict, score, duration, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            test_data.get('test_id', ''),
            test_data.get('timestamp', datetime.now().isoformat()),
            test_data.get('requirement', ''),
            test_data.get('status', 'completed'),
            test_data.get('verdict', 'N/A'),
            test_data.get('score', 0),
            test_data.get('duration', 0),
            json.dumps(test_data.get('metadata', {}))
        ))

        run_id = cursor.lastrowid

        # Save test cases
        for case in test_data.get('test_cases', []):
            cursor.execute("""
                INSERT INTO test_cases (run_id, name, suite, status, start_time, end_time, output)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id,
                case.get('name', ''),
                case.get('suite', ''),
                case.get('status', 'completed'),
                case.get('start_time', ''),
                case.get('end_time', ''),
                case.get('output', '')
            ))

            case_id = cursor.lastrowid

            # Save metrics
            for metric_name, metric_value in case.get('metrics', {}).items():
                if isinstance(metric_value, (int, float)):
                    cursor.execute("""
                        INSERT INTO metrics (run_id, case_id, name, value, unit, category, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        run_id,
                        case_id,
                        metric_name,
                        metric_value,
                        case.get('unit', ''),
                        case.get('suite', ''),
                        datetime.now().isoformat()
                    ))

        self.conn.commit()
        return run_id

    def get_test_runs(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get test runs from database.

        Args:
            limit: Maximum number of runs to return
            offset: Number of runs to skip

        Returns:
            List of test runs
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, test_id, timestamp, requirement, status, verdict, score, duration
            FROM test_runs
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))

        runs = []
        for row in cursor.fetchall():
            runs.append({
                'id': row[0],
                'test_id': row[1],
                'timestamp': row[2],
                'requirement': row[3],
                'status': row[4],
                'verdict': row[5],
                'score': row[6],
                'duration': row[7]
            })

        return runs

    def get_metric_history(self, metric_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get historical data for a specific metric.

        Args:
            metric_name: Metric name
            limit: Maximum number of data points

        Returns:
            List of metric values with timestamps
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT m.timestamp, m.value, m.unit, r.test_id
            FROM metrics m
            JOIN test_runs r ON m.run_id = r.id
            WHERE m.name = ?
            ORDER BY m.timestamp DESC
            LIMIT ?
        """, (metric_name, limit))

        history = []
        for row in cursor.fetchall():
            history.append({
                'timestamp': row[0],
                'value': row[1],
                'unit': row[2],
                'test_id': row[3]
            })

        return history

    def get_metrics_for_run(self, run_id: int) -> List[Dict[str, Any]]:
        """
        Get all metrics for a test run.

        Args:
            run_id: Test run ID

        Returns:
            List of metrics
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name, value, unit, category, timestamp
            FROM metrics
            WHERE run_id = ?
            ORDER BY timestamp
        """, (run_id,))

        metrics = []
        for row in cursor.fetchall():
            metrics.append({
                'name': row[0],
                'value': row[1],
                'unit': row[2],
                'category': row[3],
                'timestamp': row[4]
            })

        return metrics

    def create_baseline(self, name: str, run_id: int, description: str = "") -> int:
        """
        Create a baseline from a test run.

        Args:
            name: Baseline name
            run_id: Test run ID to use as baseline
            description: Baseline description

        Returns:
            Baseline ID
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO baselines (name, run_id, created_at, description)
            VALUES (?, ?, ?, ?)
        """, (name, run_id, datetime.now().isoformat(), description))

        self.conn.commit()
        return cursor.lastrowid

    def get_baseline(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get baseline by name.

        Args:
            name: Baseline name

        Returns:
            Baseline data or None
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT b.id, b.run_id, b.created_at, b.description,
                   r.test_id, r.timestamp, r.score
            FROM baselines b
            JOIN test_runs r ON b.run_id = r.id
            WHERE b.name = ?
        """, (name,))

        row = cursor.fetchone()
        if not row:
            return None

        return {
            'id': row[0],
            'run_id': row[1],
            'created_at': row[2],
            'description': row[3],
            'test_id': row[4],
            'timestamp': row[5],
            'score': row[6]
        }

    def get_trend_analysis(self, metric_name: str, days: int = 7) -> Dict[str, Any]:
        """
        Analyze trend for a metric over time.

        Args:
            metric_name: Metric name
            days: Number of days to analyze

        Returns:
            Trend analysis
        """
        from datetime import timedelta

        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT AVG(value), MIN(value), MAX(value), COUNT(*)
            FROM metrics
            WHERE name = ? AND timestamp >= ?
        """, (metric_name, cutoff))

        row = cursor.fetchone()

        return {
            'metric': metric_name,
            'period_days': days,
            'avg': row[0] or 0,
            'min': row[1] or 0,
            'max': row[2] or 0,
            'count': row[3] or 0
        }

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
