from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


def test_home_page():
    response = client.get("/")

    assert response.status_code == 200
    assert "NetScope" in response.text


def test_history_page():
    response = client.get("/history")

    assert response.status_code == 200


def test_local_api():
    response = client.get("/api/local")

    assert response.status_code == 200

    data = response.json()

    assert "hostname" in data
    assert "local_ip" in data
    assert "os" in data


def test_dns_api():
    response = client.get("/api/dns?host=example.com")

    assert response.status_code == 200

    data = response.json()

    assert "success" in data
    assert "hostname" in data


def test_invalid_tcp_port():
    response = client.get("/api/tcp?host=example.com&port=99999")

    assert response.status_code == 400


def test_invalid_http_url():
    response = client.get("/api/http?url=ftp://example.com")

    assert response.status_code == 400