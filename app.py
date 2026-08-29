import json
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from network_checks import get_local_info

from config import (
    DEFAULT_DNS_HOST,
    DEFAULT_HTTP_URL,
    DEFAULT_PING_HOST,
    DEFAULT_TCP_HOST,
    DEFAULT_TCP_PORT,
)
from database import get_diagnostics, initialize_database, save_diagnostic
from diagnostics import run_diagnostics

app = FastAPI(
    title="NetScope",
    description="Lightweight network diagnostics and monitoring application",
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

initialize_database()


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@app.get("/history")
def history(request: Request):
    records = get_diagnostics()

    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "records": records,
        },
    )

@app.get("/api/local")
def local_info():
    return get_local_info()


@app.get("/api/diagnostics")
def diagnostics():
    results = run_diagnostics(
        dns_host=DEFAULT_DNS_HOST,
        tcp_host=DEFAULT_TCP_HOST,
        tcp_port=DEFAULT_TCP_PORT,
        http_url=DEFAULT_HTTP_URL,
        ping_host_name=DEFAULT_PING_HOST,
    )

    timestamp = datetime.now(timezone.utc).isoformat()

    save_diagnostic(
        timestamp=timestamp,
        status=results["overall_status"],
        results=json.dumps(results),
    )

    return {
        "timestamp": timestamp,
        **results,
    }


@app.get("/api/dns")
def dns_check(host: str = DEFAULT_DNS_HOST):
    if not host.strip():
        raise HTTPException(status_code=400, detail="Host cannot be empty")

    from network_checks import dns_lookup

    return dns_lookup(host)


@app.get("/api/tcp")
def tcp_check(host: str = DEFAULT_TCP_HOST, port: int = DEFAULT_TCP_PORT):
    if not host.strip():
        raise HTTPException(status_code=400, detail="Host cannot be empty")

    if not 1 <= port <= 65535:
        raise HTTPException(
            status_code=400,
            detail="Port must be between 1 and 65535",
        )

    from network_checks import tcp_check as run_tcp_check

    return run_tcp_check(host, port)


@app.get("/api/http")
def http_check(url: str = DEFAULT_HTTP_URL):
    if not url.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=400,
            detail="URL must start with http:// or https://",
        )

    from network_checks import http_check as run_http_check

    return run_http_check(url)


@app.get("/api/ping")
def ping_check(host: str = DEFAULT_PING_HOST):
    if not host.strip():
        raise HTTPException(status_code=400, detail="Host cannot be empty")

    from network_checks import ping_host

    return ping_host(host)