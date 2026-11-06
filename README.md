# Py Ping Tool (`py-ping-tool`)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)

A robust, enterprise-grade cross-platform Python CLI ping utility that behaves like the system `ping` command with real-time output streaming, advanced packet statistics parsing, JSON export, and seamless compatibility across **Linux, macOS, and Windows**.

---

## Features

- **Real-Time Output Streaming**: Streams ping responses live to the terminal as packets arrive.
- **Cross-Platform**: Automatically uses platform-native syntax (`-c`/`-W` on Unix, `-n`/`-w` on Windows).
- **JSON Output Mode (`--json`)**: Export structured network metrics and raw output for automation and monitoring pipelines.
- **Verbose Logging (`-v`)**: Display underlying command execution details and timing diagnostics.
- **Graceful Interruption**: Catch `Ctrl+C` and cleanly compute partial summary statistics from accumulated output.
- **Zero Heavy Dependencies**: Built purely on standard library primitives (`subprocess`, `argparse`, `re`, `json`).
- **CLI & API Ready**: Can be invoked via command line (`py-ping`) or imported as a Python package.

---

## Installation

Clone the repository and install it locally using `pip`:

```bash
git clone https://github.com/zoly-zoly/Ping-Tool.git
cd py-ping-tool
pip install .
```

For development (including testing tools):
```bash
pip install -e .[dev]
```

---

## Usage

### Command Line Interface

```bash
# Ping a host with default settings (4 packets on Unix, continuous on Windows)
py-ping google.com

# Ping with a custom packet count
py-ping 8.8.8.8 -c 5

# Output results as structured JSON (great for scripts/monitoring)
py-ping 1.1.1.1 -c 3 --json

# Enable verbose logging
py-ping localhost -c 2 -v

# Ping with custom timeout (in seconds)
py-ping 1.1.1.1 -t 3

# Specify packet payload size in bytes
py-ping localhost -s 64
```

### Python API

```python
from ping_tool.core import execute_ping

# Define a real-time output callback
def handle_line(line):
    print(f"[LIVE] {line}")

# Execute ping and get a PingResult object
result = execute_ping("127.0.0.1", count=3, on_output=handle_line)

print(f"Packet Loss: {result.packet_loss}%")
print(f"Average RTT: {result.rtt_avg}ms")

# Export as JSON string
print(result.to_json(indent=2))
```

---

## Running Tests

Run unit tests with `pytest`:

```bash
pytest
```

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
