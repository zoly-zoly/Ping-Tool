import sys
import pytest
from ping_tool.core import build_ping_command, PingResult, execute_ping

def test_build_ping_command_linux(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    cmd = build_ping_command("127.0.0.1", count=3, timeout=2, interval=1, size=64)
    assert cmd == ["ping", "-c", "3", "-W", "2", "-i", "1", "-s", "64", "127.0.0.1"]

def test_build_ping_command_windows(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    cmd = build_ping_command("127.0.0.1", count=4, timeout=2, size=32)
    assert cmd == ["ping", "-n", "4", "-w", "2000", "-l", "32", "127.0.0.1"]

def test_ping_result_parsing_linux():
    sample_output = """PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.032 ms
64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.028 ms

--- 127.0.0.1 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1001ms
rtt min/avg/max/mdev = 0.028/0.030/0.032/0.002 ms"""

    result = PingResult("127.0.0.1", sample_output, 0)
    assert result.packets_transmitted == 2
    assert result.packets_received == 2
    assert result.packet_loss == 0.0
    assert result.rtt_min == 0.028
    assert result.rtt_avg == 0.030
    assert result.rtt_max == 0.032
    assert result.rtt_mdev == 0.002

    d = result.to_dict()
    assert d["host"] == "127.0.0.1"
    assert d["packet_loss"] == 0.0
    
    j = result.to_json()
    assert "127.0.0.1" in j

def test_ping_result_parsing_windows():
    sample_output = """
Pinging 127.0.0.1 with 32 bytes of data:
Reply from 127.0.0.1: bytes=32 time<1ms TTL=128
Reply from 127.0.0.1: bytes=32 time<1ms TTL=128

Ping statistics for 127.0.0.1:
    Packets: Sent = 2, Received = 2, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 0ms, Maximum = 0ms, Average = 0ms
"""
    result = PingResult("127.0.0.1", sample_output, 0)
    assert result.packets_transmitted == 2
    assert result.packets_received == 2
    assert result.packet_loss == 0.0
    assert result.rtt_min == 0.0
    assert result.rtt_max == 0.0
    assert result.rtt_avg == 0.0
