from diagnostics import calculate_overall_status


def test_all_checks_healthy():
    results = {
        "internet": {"success": True},
        "dns": {"success": True},
        "tcp": {"success": True},
        "http": {"success": True},
        "ping": {"success": True},
    }

    assert calculate_overall_status(results) == "Healthy"


def test_degraded_status():
    results = {
        "internet": {"success": True},
        "dns": {"success": True},
        "tcp": {"success": True},
        "http": {"success": False},
        "ping": {"success": False},
    }

    assert calculate_overall_status(results) == "Degraded"


def test_unhealthy_status():
    results = {
        "internet": {"success": False},
        "dns": {"success": False},
        "tcp": {"success": False},
        "http": {"success": True},
        "ping": {"success": False},
    }

    assert calculate_overall_status(results) == "Unhealthy"


def test_empty_results_are_unhealthy():
    results = {
        "internet": {},
        "dns": {},
        "tcp": {},
        "http": {},
        "ping": {},
    }

    assert calculate_overall_status(results) == "Unhealthy"