import platform
import socket
import subprocess
import time
from typing import Any


def get_local_info() -> dict[str, str]:
    """Return basic information about the local machine."""
    hostname = socket.gethostname()
    local_ip = "Unavailable"

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            local_ip = sock.getsockname()[0]
    except OSError:
        try:
            local_ip = socket.gethostbyname(hostname)
        except socket.gaierror:
            pass

    return {
        "hostname": hostname,
        "local_ip": local_ip,
        "os": platform.system(),
    }


def check_internet(host: str = "8.8.8.8", port: int = 53, timeout: float = 3.0) -> dict[str, Any]:
    """Check whether a TCP connection to a public endpoint can be established."""
    start = time.perf_counter()

    try:
        with socket.create_connection((host, port), timeout=timeout):
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

            return {
                "success": True,
                "host": host,
                "port": port,
                "latency_ms": elapsed_ms,
                "error": None,
            }

    except OSError as exc:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        return {
            "success": False,
            "host": host,
            "port": port,
            "latency_ms": elapsed_ms,
            "error": str(exc),
        }


def dns_lookup(hostname: str = "example.com") -> dict[str, Any]:
    """Resolve a hostname and measure DNS lookup time."""
    start = time.perf_counter()

    try:
        addresses = socket.getaddrinfo(hostname, None)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        ips = sorted(
            {
                result[4][0]
                for result in addresses
                if result[4]
            }
        )

        return {
            "success": True,
            "hostname": hostname,
            "addresses": ips,
            "response_time_ms": elapsed_ms,
            "error": None,
        }

    except socket.gaierror as exc:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        return {
            "success": False,
            "hostname": hostname,
            "addresses": [],
            "response_time_ms": elapsed_ms,
            "error": str(exc),
        }


def tcp_check(
    host: str,
    port: int,
    timeout: float = 3.0,
) -> dict[str, Any]:
    """Test whether a TCP service accepts a connection."""
    start = time.perf_counter()

    try:
        with socket.create_connection((host, port), timeout=timeout):
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

            return {
                "success": True,
                "host": host,
                "port": port,
                "response_time_ms": elapsed_ms,
                "error": None,
            }

    except OSError as exc:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        return {
            "success": False,
            "host": host,
            "port": port,
            "response_time_ms": elapsed_ms,
            "error": str(exc),
        }


def http_check(
    url: str = "https://example.com",
    timeout: float = 5.0,
) -> dict[str, Any]:
    """Check an HTTP endpoint using the standard library."""
    from urllib.request import Request, urlopen

    start = time.perf_counter()

    try:
        request = Request(
            url,
            headers={
                "User-Agent": "NetScope/0.1",
            },
        )

        with urlopen(request, timeout=timeout) as response:
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

            return {
                "success": True,
                "url": url,
                "status_code": response.status,
                "response_time_ms": elapsed_ms,
                "error": None,
            }

    except Exception as exc:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        return {
            "success": False,
            "url": url,
            "status_code": None,
            "response_time_ms": elapsed_ms,
            "error": str(exc),
        }


def ping_host(
    host: str = "8.8.8.8",
    count: int = 4,
) -> dict[str, Any]:
    """Measure basic latency and packet loss using the system ping command."""
    count = max(1, min(count, 10))

    command = [
        "ping",
        "-n" if platform.system() == "Windows" else "-c",
        str(count),
        host,
    ]

    start = time.perf_counter()

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=max(10, count * 3),
        )

        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        output = result.stdout + result.stderr
        packet_loss = _extract_packet_loss(output)

        return {
            "success": result.returncode == 0,
            "host": host,
            "packet_loss_percent": packet_loss,
            "total_time_ms": elapsed_ms,
            "output": output.strip(),
            "error": None if result.returncode == 0 else "Ping failed",
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "host": host,
            "packet_loss_percent": None,
            "total_time_ms": None,
            "output": "",
            "error": "Ping timed out",
        }

    except OSError as exc:
        return {
            "success": False,
            "host": host,
            "packet_loss_percent": None,
            "total_time_ms": None,
            "output": "",
            "error": str(exc),
        }


def _extract_packet_loss(output: str) -> float | None:
    """Extract packet-loss percentage from ping output."""
    import re

    patterns = [
        r"\((\d+(?:\.\d+)?)%\s*loss\)",
        r"(\d+(?:\.\d+)?)%\s*loss",
    ]

    for pattern in patterns:
        match = re.search(pattern, output, re.IGNORECASE)

        if match:
            return float(match.group(1))

    return None