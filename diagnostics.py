from typing import Any

from network_checks import (
    check_internet,
    dns_lookup,
    get_local_info,
    http_check,
    ping_host,
    tcp_check,
)


def run_diagnostics(
    dns_host: str = "example.com",
    tcp_host: str = "example.com",
    tcp_port: int = 443,
    http_url: str = "https://example.com",
    ping_host_name: str = "8.8.8.8",
) -> dict[str, Any]:
    """Run the main NetScope diagnostics."""
    results = {
        "local": get_local_info(),
        "internet": check_internet(),
        "dns": dns_lookup(dns_host),
        "tcp": tcp_check(tcp_host, tcp_port),
        "http": http_check(http_url),
        "ping": ping_host(ping_host_name),
    }

    results["analysis"] = analyze_results(results)
    results["overall_status"] = calculate_overall_status(results)

    return results


def calculate_overall_status(results: dict[str, Any]) -> str:
    """Calculate an overall diagnostic status."""
    checks = [
        results.get("internet", {}).get("success"),
        results.get("dns", {}).get("success"),
        results.get("tcp", {}).get("success"),
        results.get("http", {}).get("success"),
        results.get("ping", {}).get("success"),
    ]

    successful = sum(check is True for check in checks)

    if successful == len(checks):
        return "Healthy"

    if successful >= 3:
        return "Degraded"

    return "Unhealthy"


def analyze_results(results: dict[str, Any]) -> dict[str, Any]:
    """Interpret raw diagnostic results."""
    findings = []
    recommendations = []

    dns_result = results.get("dns", {})
    tcp_result = results.get("tcp", {})
    http_result = results.get("http", {})
    ping_result = results.get("ping", {})
    internet_result = results.get("internet", {})

    # Internet
    if not internet_result.get("success"):
        findings.append("Internet connectivity could not be established.")
        recommendations.append(
            "Check your network connection, router, Wi-Fi, or Ethernet connection."
        )

    # DNS
    if dns_result.get("success"):
        dns_time = dns_result.get("response_time_ms", 0)

        if dns_time < 100:
            findings.append("DNS resolution is fast.")
        elif dns_time < 300:
            findings.append("DNS resolution is moderately slow.")
            recommendations.append(
                "Consider checking DNS server performance if slow resolution persists."
            )
        else:
            findings.append("DNS resolution is slow.")
            recommendations.append(
                "Try another DNS resolver or investigate DNS/network latency."
            )
    else:
        findings.append("DNS resolution failed.")
        recommendations.append(
            "Check DNS configuration and verify that the hostname is correct."
        )

    # TCP
    if tcp_result.get("success"):
        tcp_time = tcp_result.get("response_time_ms", 0)

        if tcp_time < 100:
            findings.append("TCP connection establishment is fast.")
        elif tcp_time < 300:
            findings.append("TCP connection establishment is moderately slow.")
        else:
            findings.append("TCP connection establishment is slow.")
            recommendations.append(
                "Investigate network latency or the destination service."
            )
    else:
        findings.append("TCP connection failed.")
        recommendations.append(
            "Verify that the host and port are correct and that the service is reachable."
        )

    # HTTP
    if http_result.get("success"):
        status_code = http_result.get("status_code")
        http_time = http_result.get("response_time_ms", 0)

        if status_code and 200 <= status_code < 300:
            findings.append(f"HTTP endpoint responded successfully with status {status_code}.")
        elif status_code and 300 <= status_code < 400:
            findings.append(f"HTTP endpoint returned a redirect ({status_code}).")
        elif status_code:
            findings.append(f"HTTP endpoint returned status {status_code}.")
            recommendations.append(
                "Check the destination endpoint and its server-side status."
            )

        if http_time > 1000:
            findings.append("HTTP response time is high.")
            recommendations.append(
                "Investigate application/server response time and network latency."
            )

    else:
        findings.append("HTTP request failed.")
        recommendations.append(
            "Verify the URL and check whether the destination service is available."
        )

    # Ping
    if ping_result.get("success"):
        packet_loss = ping_result.get("packet_loss_percent")
        output = ping_result.get("output", "")

        average_latency = _extract_average_latency(output)

        if packet_loss is not None:
            if packet_loss == 0:
                findings.append("No packet loss was detected.")
            elif packet_loss < 5:
                findings.append(f"Low packet loss detected ({packet_loss}%).")
                recommendations.append(
                    "Monitor the connection if packet loss continues."
                )
            else:
                findings.append(f"High packet loss detected ({packet_loss}%).")
                recommendations.append(
                    "Check Wi-Fi signal, network congestion, router health, or the network path."
                )

        if average_latency is not None:
            if average_latency < 50:
                findings.append(f"Average latency is good ({average_latency} ms).")
            elif average_latency < 150:
                findings.append(
                    f"Average latency is moderate ({average_latency} ms)."
                )
            else:
                findings.append(f"Average latency is high ({average_latency} ms).")
                recommendations.append(
                    "Investigate network congestion or routing latency."
                )

    else:
        findings.append("Ping test failed.")
        recommendations.append(
            "Check whether the destination allows ICMP traffic and verify connectivity."
        )

    # Remove duplicate recommendations while preserving order.
    recommendations = list(dict.fromkeys(recommendations))

    return {
        "findings": findings,
        "recommendations": recommendations,
    }


def _extract_average_latency(output: str) -> float | None:
    """Extract average ping latency from Windows or Unix output."""
    import re

    patterns = [
        r"Average\s*=\s*(\d+(?:\.\d+)?)ms",
        r"avg(?:erage)?[^\d]*(\d+(?:\.\d+)?)\s*ms",
    ]

    for pattern in patterns:
        match = re.search(pattern, output, re.IGNORECASE)

        if match:
            return float(match.group(1))

    return None