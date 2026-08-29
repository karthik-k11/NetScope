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