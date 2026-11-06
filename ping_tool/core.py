import sys
import subprocess
import re
import json
from typing import List, Dict, Any, Callable, Optional

class PingResult:
    def __init__(self, host: str, output: str, exit_code: int):
        self.host = host
        self.output = output
        self.exit_code = exit_code
        self.packets_transmitted = 0
        self.packets_received = 0
        self.packet_loss = 100.0
        self.rtt_min = None
        self.rtt_avg = None
        self.rtt_max = None
        self.rtt_mdev = None
        self._parse_stats()

    def _parse_stats(self):
        if "Packets: Sent" in self.output or "Approximate round trip" in self.output or "Pinging " in self.output:
            sent_match = re.search(r"Sent\s*=\s*(\d+)", self.output, re.IGNORECASE)
            recv_match = re.search(r"Received\s*=\s*(\d+)", self.output, re.IGNORECASE)
            loss_match = re.search(r"(\d+)%\s*loss", self.output, re.IGNORECASE)
            
            if sent_match:
                self.packets_transmitted = int(sent_match.group(1))
            if recv_match:
                self.packets_received = int(recv_match.group(1))
            if loss_match:
                self.packet_loss = float(loss_match.group(1))

            rtt_match = re.search(r"Minimum\s*=\s*(\d+)ms,\s*Maximum\s*=\s*(\d+)ms,\s*Average\s*=\s*(\d+)ms", self.output, re.IGNORECASE)
            if rtt_match:
                self.rtt_min = float(rtt_match.group(1))
                self.rtt_max = float(rtt_match.group(2))
                self.rtt_avg = float(rtt_match.group(3))
        else:
            trans_match = re.search(r"(\d+)\s+packets transmitted,\s+(\d+)\s+(?:packets\s+)?received", self.output, re.IGNORECASE)
            if trans_match:
                self.packets_transmitted = int(trans_match.group(1))
                self.packets_received = int(trans_match.group(2))

            loss_match = re.search(r"([\d.]+)%\s+packet loss", self.output, re.IGNORECASE)
            if loss_match:
                self.packet_loss = float(loss_match.group(1))

            rtt_match = re.search(r"(?:rtt|round-trip)\s+min/avg/max/(?:mdev|stddev)\s*=\s*([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)\s*ms", self.output, re.IGNORECASE)
            if rtt_match:
                self.rtt_min = float(rtt_match.group(1))
                self.rtt_avg = float(rtt_match.group(2))
                self.rtt_max = float(rtt_match.group(3))
                self.rtt_mdev = float(rtt_match.group(4))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "host": self.host,
            "packets_transmitted": self.packets_transmitted,
            "packets_received": self.packets_received,
            "packet_loss": self.packet_loss,
            "rtt_min": self.rtt_min,
            "rtt_avg": self.rtt_avg,
            "rtt_max": self.rtt_max,
            "rtt_mdev": self.rtt_mdev,
            "exit_code": self.exit_code,
            "output": self.output
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


def build_ping_command(
    target: str,
    count: Optional[int] = None,
    timeout: Optional[int] = None,
    interval: Optional[int] = None,
    size: Optional[int] = None
) -> List[str]:
    is_windows = sys.platform.startswith("win")
    cmd = ["ping"]

    if is_windows:
        if count is not None:
            cmd.extend(["-n", str(count)])
        if timeout is not None:
            cmd.extend(["-w", str(int(timeout * 1000))])
        if size is not None:
            cmd.extend(["-l", str(size)])
    else:
        if count is not None:
            cmd.extend(["-c", str(count)])
        if timeout is not None:
            cmd.extend(["-W", str(timeout)])
        if interval is not None:
            cmd.extend(["-i", str(interval)])
        if size is not None:
            cmd.extend(["-s", str(size)])

    cmd.append(target)
    return cmd


def execute_ping(
    target: str,
    count: Optional[int] = None,
    timeout: Optional[int] = None,
    interval: Optional[int] = None,
    size: Optional[int] = None,
    on_output: Optional[Callable[[str], None]] = None,
    verbose: bool = False
) -> PingResult:
    cmd = build_ping_command(target, count=count, timeout=timeout, interval=interval, size=size)
    
    if verbose and on_output:
        on_output(f"Executing command: {' '.join(cmd)}")

    output_lines = []
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                cleaned_line = line.rstrip()
                output_lines.append(cleaned_line)
                if on_output:
                    on_output(cleaned_line)
                    
        return_code = process.wait()
    except Exception as e:
        err_msg = f"Error executing ping: {e}"
        output_lines.append(err_msg)
        if on_output:
            on_output(err_msg)
        return_code = 1

    full_output = "\n".join(output_lines)
    return PingResult(host=target, output=full_output, exit_code=return_code)
