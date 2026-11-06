import argparse
import sys
from ping_tool.core import execute_ping, PingResult

def main():
    parser = argparse.ArgumentParser(
        description="A robust, cross-platform Python CLI ping utility with real-time output streaming and JSON statistics."
    )
    parser.add_argument("target", help="Target host or IP address to ping")
    parser.add_argument("-c", "--count", type=int, default=None, help="Number of packets to send")
    parser.add_argument("-t", "--timeout", type=int, default=None, help="Timeout in seconds")
    parser.add_argument("-i", "--interval", type=int, default=None, help="Interval between packets in seconds (Linux/macOS)")
    parser.add_argument("-s", "--size", type=int, default=None, help="Packet payload size in bytes")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    output_lines = []

    def handle_output(line: str):
        if not args.json:
            print(line)
            sys.stdout.flush()
        output_lines.append(line)

    try:
        result = execute_ping(
            target=args.target,
            count=args.count,
            timeout=args.timeout,
            interval=args.interval,
            size=args.size,
            on_output=handle_output,
            verbose=args.verbose
        )
        if args.json:
            print(result.to_json())
        sys.exit(result.exit_code)
    except KeyboardInterrupt:
        if not args.json:
            print("\n--- Ping statistics (Interrupted) ---")
            full_output = "\n".join(output_lines)
            partial_result = PingResult(host=args.target, output=full_output, exit_code=0)
            print(f"Packets transmitted: {partial_result.packets_transmitted}, Received: {partial_result.packets_received}, Loss: {partial_result.packet_loss}%")
        else:
            full_output = "\n".join(output_lines)
            partial_result = PingResult(host=args.target, output=full_output, exit_code=0)
            print(partial_result.to_json())
        sys.exit(0)

if __name__ == "__main__":
    main()
