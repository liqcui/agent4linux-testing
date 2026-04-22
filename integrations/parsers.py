"""
Advanced parsers for various test suite outputs.
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ParsedMetric:
    """Structured metric data."""
    name: str
    value: float
    unit: str
    category: str
    metadata: Dict[str, Any] = None


class BaseParser:
    """Base parser class."""

    def parse(self, output: str) -> Dict[str, Any]:
        """
        Parse test output.

        Args:
            output: Raw test output

        Returns:
            Parsed metrics dictionary
        """
        raise NotImplementedError


class RTTestsParser(BaseParser):
    """Parser for rt-tests output (cyclictest, etc.)."""

    def parse(self, output: str) -> Dict[str, Any]:
        """Parse rt-tests cyclictest output."""
        metrics = {
            "latencies": {},
            "statistics": {},
            "threads": [],
            "smi_count": 0
        }

        lines = output.split("\n")

        for line in lines:
            # Parse latency values
            # Format: "T: 0 ( 1234) P:99 I:1000 C:  60000 Min:   2 Act:   5 Avg:   6 Max:  18"
            if line.strip().startswith("T:"):
                thread_data = self._parse_thread_line(line)
                if thread_data:
                    metrics["threads"].append(thread_data)

            # Parse summary statistics
            # Format: "Min Latencies: 2"
            if "Min Latencies:" in line:
                value = self._extract_number(line)
                if value is not None:
                    metrics["latencies"]["min"] = value

            if "Avg Latencies:" in line:
                value = self._extract_number(line)
                if value is not None:
                    metrics["latencies"]["avg"] = value

            if "Max Latencies:" in line:
                value = self._extract_number(line)
                if value is not None:
                    metrics["latencies"]["max"] = value

            # Parse SMI count
            if "SMI count:" in line:
                value = self._extract_number(line)
                if value is not None:
                    metrics["smi_count"] = value

        # Calculate statistics
        if metrics["threads"]:
            metrics["statistics"] = self._calculate_statistics(metrics["threads"])

        return metrics

    def _parse_thread_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse individual thread statistics line."""
        # T: 0 ( 1234) P:99 I:1000 C:  60000 Min:   2 Act:   5 Avg:   6 Max:  18
        pattern = r"T:\s*(\d+).*P:(\d+).*Min:\s*(\d+).*Avg:\s*(\d+).*Max:\s*(\d+)"
        match = re.search(pattern, line)

        if match:
            return {
                "thread_id": int(match.group(1)),
                "priority": int(match.group(2)),
                "min_latency": int(match.group(3)),
                "avg_latency": int(match.group(4)),
                "max_latency": int(match.group(5))
            }
        return None

    def _extract_number(self, line: str) -> Optional[float]:
        """Extract numeric value from line."""
        numbers = re.findall(r'\d+\.?\d*', line)
        if numbers:
            return float(numbers[0])
        return None

    def _calculate_statistics(self, threads: List[Dict]) -> Dict[str, float]:
        """Calculate aggregate statistics."""
        if not threads:
            return {}

        max_latencies = [t["max_latency"] for t in threads]
        avg_latencies = [t["avg_latency"] for t in threads]

        import statistics

        return {
            "overall_max": max(max_latencies),
            "overall_avg": statistics.mean(avg_latencies),
            "max_std_dev": statistics.stdev(max_latencies) if len(max_latencies) > 1 else 0,
            "thread_count": len(threads)
        }


class StressNGParser(BaseParser):
    """Parser for stress-ng output."""

    def parse(self, output: str) -> Dict[str, Any]:
        """Parse stress-ng output."""
        metrics = {
            "stressors": {},
            "system_metrics": {},
            "summary": {}
        }

        lines = output.split("\n")

        for line in lines:
            # Parse stressor results
            # Format: "stress-ng: info:  [12345] vm   125000  60.01  180.23  58.45  2083.32  524.45"
            if "stress-ng: info:" in line and not any(x in line for x in ["dispatching", "successful"]):
                stressor_data = self._parse_stressor_line(line)
                if stressor_data:
                    metrics["stressors"][stressor_data["name"]] = stressor_data

            # Parse bandwidth/throughput metrics
            # Format: "stress-ng: info:  [12345] memcpy:   12.5 GB/sec"
            if "GB/sec" in line or "MB/sec" in line:
                name, value, unit = self._parse_throughput_line(line)
                if name:
                    if "bandwidth" not in metrics:
                        metrics["bandwidth"] = {}
                    metrics["bandwidth"][name] = {"value": value, "unit": unit}

        return metrics

    def _parse_stressor_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse stressor result line."""
        # Extract stressor name and metrics
        parts = line.split()

        try:
            # Find the stressor name (after PID in brackets)
            stressor_start = False
            stressor_name = None

            for i, part in enumerate(parts):
                if part.endswith("]"):
                    stressor_start = True
                    continue
                if stressor_start and not part.replace(".", "").isdigit():
                    stressor_name = part
                    break

            if not stressor_name:
                return None

            # Extract numeric values (bogo ops, times, ops/s)
            numbers = [float(p) for p in parts if p.replace(".", "").replace("-", "").isdigit()]

            if len(numbers) >= 5:
                return {
                    "name": stressor_name,
                    "bogo_ops": int(numbers[0]),
                    "real_time": numbers[1],
                    "usr_time": numbers[2],
                    "sys_time": numbers[3],
                    "bogo_ops_per_sec_real": numbers[4],
                    "bogo_ops_per_sec_cpu": numbers[5] if len(numbers) > 5 else 0
                }
        except (ValueError, IndexError):
            pass

        return None

    def _parse_throughput_line(self, line: str) -> tuple:
        """Parse throughput/bandwidth line."""
        # Extract: stressor_name, value, unit
        parts = line.split(":")
        if len(parts) < 2:
            return None, None, None

        name_part = parts[-2].strip().split()[-1]
        value_part = parts[-1].strip()

        # Extract value and unit
        match = re.search(r'([\d.]+)\s*(GB/sec|MB/sec|Gbps|Mbps)', value_part)
        if match:
            return name_part, float(match.group(1)), match.group(2)

        return None, None, None


class NetworkParser(BaseParser):
    """Parser for network test outputs (iperf3, netperf, qperf)."""

    def parse(self, output: str) -> Dict[str, Any]:
        """Parse network test output."""
        metrics = {
            "throughput": {},
            "latency": {},
            "connections": {},
            "packet_loss": {}
        }

        # Detect test type
        if "iperf3" in output.lower() or "iperf version" in output.lower():
            metrics.update(self._parse_iperf3(output))
        elif "netperf" in output.lower():
            metrics.update(self._parse_netperf(output))
        elif "qperf" in output.lower():
            metrics.update(self._parse_qperf(output))

        return metrics

    def _parse_iperf3(self, output: str) -> Dict[str, Any]:
        """Parse iperf3 output."""
        data = {}

        # Parse throughput
        # Format: "[ ID] Interval           Transfer     Bitrate"
        #         "[SUM]   0.00-10.00  sec  1.10 GBytes  944 Mbits/sec"
        for line in output.split("\n"):
            if "[SUM]" in line or "sender" in line or "receiver" in line:
                match = re.search(r'([\d.]+)\s+([KMG]?)bits/sec', line)
                if match:
                    value = float(match.group(1))
                    unit = match.group(2) + "bits/sec"

                    # Convert to Mbps
                    if "Gbits" in unit:
                        value *= 1000
                    elif "Kbits" in unit:
                        value /= 1000

                    if "sender" in line:
                        data["throughput_tx_mbps"] = value
                    elif "receiver" in line:
                        data["throughput_rx_mbps"] = value
                    elif "[SUM]" in line:
                        data["throughput_total_mbps"] = value

            # Parse packet loss (UDP)
            if "%" in line and "lost" in line.lower():
                match = re.search(r'([\d.]+)%', line)
                if match:
                    data["packet_loss_percent"] = float(match.group(1))

        return data

    def _parse_netperf(self, output: str) -> Dict[str, Any]:
        """Parse netperf output."""
        data = {}

        # Parse throughput (TCP_STREAM)
        # Look for throughput in Mbps
        match = re.search(r'([\d.]+)\s+Mbps', output)
        if match:
            data["throughput_mbps"] = float(match.group(1))

        # Parse transaction rate (TCP_RR)
        match = re.search(r'([\d.]+)\s+trans/s', output)
        if match:
            data["transactions_per_sec"] = float(match.group(1))

        return data

    def _parse_qperf(self, output: str) -> Dict[str, Any]:
        """Parse qperf output."""
        data = {}

        lines = output.split("\n")
        for line in lines:
            # Parse bandwidth
            if "bw" in line or "bandwidth" in line.lower():
                match = re.search(r'([\d.]+)\s+([KMG]B)/sec', line)
                if match:
                    data["bandwidth"] = {
                        "value": float(match.group(1)),
                        "unit": match.group(2) + "/sec"
                    }

            # Parse latency
            if "latency" in line.lower():
                match = re.search(r'([\d.]+)\s+(us|ms)', line)
                if match:
                    data["latency_us"] = float(match.group(1))
                    if match.group(2) == "ms":
                        data["latency_us"] *= 1000

        return data


class IOParser(BaseParser):
    """Parser for I/O test outputs (fio, iozone)."""

    def parse(self, output: str) -> Dict[str, Any]:
        """Parse I/O test output."""
        metrics = {
            "iops": {},
            "bandwidth": {},
            "latency": {}
        }

        if "fio" in output.lower():
            metrics.update(self._parse_fio(output))
        elif "iozone" in output.lower():
            metrics.update(self._parse_iozone(output))

        return metrics

    def _parse_fio(self, output: str) -> Dict[str, Any]:
        """Parse fio output."""
        data = {}

        lines = output.split("\n")
        for line in lines:
            # Parse IOPS
            if "iops=" in line:
                match = re.search(r'iops=([\d.]+)([kK]?)', line)
                if match:
                    iops = float(match.group(1))
                    if match.group(2).lower() == 'k':
                        iops *= 1000
                    data["iops"] = iops

            # Parse bandwidth
            if "bw=" in line or "BW=" in line:
                match = re.search(r'[bB][wW]=([\d.]+)([KMG]iB/s|[KMG]B/s)', line)
                if match:
                    bw = float(match.group(1))
                    unit = match.group(2)

                    # Convert to MB/s
                    if "KiB" in unit or "KB" in unit:
                        bw /= 1024
                    elif "GiB" in unit or "GB" in unit:
                        bw *= 1024

                    data["bandwidth_mbps"] = bw

            # Parse latency
            if "lat (" in line or "latency" in line.lower():
                # Parse average latency
                match = re.search(r'avg=([\d.]+)', line)
                if match:
                    data["latency_avg_us"] = float(match.group(1))

                # Parse percentiles
                match = re.search(r'99\.00th=\[([\d]+)\]', line)
                if match:
                    data["latency_p99_us"] = float(match.group(1))

        return data

    def _parse_iozone(self, output: str) -> Dict[str, Any]:
        """Parse iozone output."""
        data = {}

        # iozone outputs tabular data
        # Parse write/read throughput
        for line in output.split("\n"):
            if "KB" in line or "MB" in line:
                # Extract numeric values
                numbers = re.findall(r'\d+', line)
                if len(numbers) >= 3:
                    # Usually: record_size, file_size, write_kb/s, read_kb/s
                    try:
                        data["write_kbps"] = int(numbers[2])
                        if len(numbers) > 3:
                            data["read_kbps"] = int(numbers[3])
                    except (ValueError, IndexError):
                        pass

        return data


class MemoryParser(BaseParser):
    """Parser for memory test outputs (STREAM, memtester)."""

    def parse(self, output: str) -> Dict[str, Any]:
        """Parse memory test output."""
        metrics = {
            "bandwidth": {},
            "errors": []
        }

        if "stream" in output.lower():
            metrics.update(self._parse_stream(output))
        elif "memtester" in output.lower():
            metrics.update(self._parse_memtester(output))

        return metrics

    def _parse_stream(self, output: str) -> Dict[str, Any]:
        """Parse STREAM benchmark output."""
        data = {}

        operations = ["Copy", "Scale", "Add", "Triad"]

        for line in output.split("\n"):
            for op in operations:
                if op in line:
                    # Format: "Copy:       12345.6    0.0123    0.0124    0.0125"
                    numbers = re.findall(r'[\d.]+', line)
                    if len(numbers) >= 2:
                        # First number is bandwidth in MB/s
                        data[f"{op.lower()}_mbps"] = float(numbers[0])

        return data

    def _parse_memtester(self, output: str) -> Dict[str, Any]:
        """Parse memtester output."""
        data = {"tests": [], "failures": []}

        for line in output.split("\n"):
            if "ok" in line.lower():
                # Extract test name
                test_name = line.split(":")[0].strip()
                data["tests"].append({"name": test_name, "status": "passed"})
            elif "fail" in line.lower() or "error" in line.lower():
                test_name = line.split(":")[0].strip()
                data["tests"].append({"name": test_name, "status": "failed"})
                data["failures"].append(test_name)

        data["total_tests"] = len(data["tests"])
        data["passed_tests"] = len([t for t in data["tests"] if t["status"] == "passed"])
        data["failed_tests"] = len(data["failures"])

        return data


class BenchmarkParser(BaseParser):
    """Parser for benchmark outputs (UnixBench, lmbench)."""

    def parse(self, output: str) -> Dict[str, Any]:
        """Parse benchmark output."""
        metrics = {
            "scores": {},
            "benchmarks": []
        }

        if "unixbench" in output.lower() or "index score" in output.lower():
            metrics.update(self._parse_unixbench(output))
        elif "lmbench" in output.lower():
            metrics.update(self._parse_lmbench(output))

        return metrics

    def _parse_unixbench(self, output: str) -> Dict[str, Any]:
        """Parse UnixBench output."""
        data = {}

        for line in output.split("\n"):
            # Parse individual benchmark scores
            if "score" in line.lower() and not "system" in line.lower():
                match = re.search(r'([\d.]+)', line)
                if match:
                    score = float(match.group(1))
                    # Determine benchmark name
                    benchmark_name = line.split()[0].strip()
                    data[f"{benchmark_name}_score"] = score

            # Parse system benchmarks index
            if "System Benchmarks Index Score" in line:
                match = re.search(r'([\d.]+)', line)
                if match:
                    data["system_index_score"] = float(match.group(1))

        return data

    def _parse_lmbench(self, output: str) -> Dict[str, Any]:
        """Parse lmbench output."""
        data = {}

        for line in output.split("\n"):
            # Parse latency measurements
            if "latency" in line.lower():
                match = re.search(r'([\d.]+)\s+(us|ns|ms)', line)
                if match:
                    latency = float(match.group(1))
                    unit = match.group(2)

                    # Convert to microseconds
                    if unit == "ns":
                        latency /= 1000
                    elif unit == "ms":
                        latency *= 1000

                    # Extract measurement type
                    measurement = line.split(":")[0].strip()
                    data[f"{measurement}_latency_us"] = latency

            # Parse bandwidth measurements
            if "bandwidth" in line.lower() or "MB/s" in line:
                match = re.search(r'([\d.]+)\s+MB/s', line)
                if match:
                    bandwidth = float(match.group(1))
                    measurement = line.split(":")[0].strip()
                    data[f"{measurement}_mbps"] = bandwidth

        return data
