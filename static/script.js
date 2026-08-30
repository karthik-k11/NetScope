const runButton = document.getElementById("runDiagnostics");

const hostnameElement = document.getElementById("hostname");
const localIpElement = document.getElementById("localIp");
const operatingSystemElement = document.getElementById("operatingSystem");

const overallStatus = document.getElementById("overallStatus");
const diagnosticTime = document.getElementById("diagnosticTime");
const errorMessage = document.getElementById("errorMessage");


const checks = {
    dns: {
        button: document.getElementById("dnsButton"),
        status: document.getElementById("dnsStatus"),
        result: document.getElementById("dnsResult"),
    },

    tcp: {
        button: document.getElementById("tcpButton"),
        status: document.getElementById("tcpStatus"),
        result: document.getElementById("tcpResult"),
    },

    http: {
        button: document.getElementById("httpButton"),
        status: document.getElementById("httpStatus"),
        result: document.getElementById("httpResult"),
    },

    ping: {
        button: document.getElementById("pingButton"),
        status: document.getElementById("pingStatus"),
        result: document.getElementById("pingResult"),
    },
};


async function loadLocalInfo() {
    try {
        const response = await fetch("/api/local");

        if (!response.ok) {
            throw new Error("Unable to load local system information.");
        }

        const data = await response.json();

        hostnameElement.textContent = data.hostname;
        localIpElement.textContent = data.local_ip;
        operatingSystemElement.textContent = data.os;

    } catch {
        hostnameElement.textContent = "Unavailable";
        localIpElement.textContent = "Unavailable";
        operatingSystemElement.textContent = "Unavailable";
    }
}


function clearError() {
    errorMessage.textContent = "";
    errorMessage.classList.add("hidden");
}


function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove("hidden");
}


function setStatus(checkName, success) {
    const check = checks[checkName];

    check.status.textContent = success ? "Healthy" : "Failed";
    check.status.className =
        `status ${success ? "success" : "failure"}`;
}


function setLoading(checkName) {
    const check = checks[checkName];

    check.status.textContent = "Testing...";
    check.status.className = "status loading";
    check.result.textContent = "Running...";
    check.button.disabled = true;
}


function finishCheck(checkName) {
    checks[checkName].button.disabled = false;
}


async function runDnsCheck() {
    const host = document.getElementById("dnsHost").value.trim();

    if (!host) {
        showError("Please enter a hostname.");
        return;
    }

    clearError();
    setLoading("dns");

    try {
        const response = await fetch(
            `/api/dns?host=${encodeURIComponent(host)}`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "DNS check failed.");
        }

        setStatus("dns", data.success);

        if (data.success) {
            checks.dns.result.textContent =
                `${data.response_time_ms} ms • ` +
                `${data.addresses.length} address(es)`;
        } else {
            checks.dns.result.textContent = data.error;
        }

    } catch (error) {
        checks.dns.status.textContent = "Error";
        checks.dns.status.className = "status failure";
        checks.dns.result.textContent = error.message;
    } finally {
        finishCheck("dns");
    }
}


async function runTcpCheck() {
    const host = document.getElementById("tcpHost").value.trim();
    const port = document.getElementById("tcpPort").value;

    if (!host) {
        showError("Please enter a TCP host.");
        return;
    }

    if (!port || port < 1 || port > 65535) {
        showError("TCP port must be between 1 and 65535.");
        return;
    }

    clearError();
    setLoading("tcp");

    try {
        const response = await fetch(
            `/api/tcp?host=${encodeURIComponent(host)}&port=${port}`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "TCP check failed.");
        }

        setStatus("tcp", data.success);

        if (data.success) {
            checks.tcp.result.textContent =
                `${data.response_time_ms} ms`;
        } else {
            checks.tcp.result.textContent = data.error;
        }

    } catch (error) {
        checks.tcp.status.textContent = "Error";
        checks.tcp.status.className = "status failure";
        checks.tcp.result.textContent = error.message;
    } finally {
        finishCheck("tcp");
    }
}


async function runHttpCheck() {
    const url = document.getElementById("httpUrl").value.trim();

    if (!url) {
        showError("Please enter a URL.");
        return;
    }

    if (!url.startsWith("http://") && !url.startsWith("https://")) {
        showError("URL must start with http:// or https://.");
        return;
    }

    clearError();
    setLoading("http");

    try {
        const response = await fetch(
            `/api/http?url=${encodeURIComponent(url)}`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "HTTP check failed.");
        }

        setStatus("http", data.success);

        if (data.success) {
            checks.http.result.textContent =
                `${data.status_code} • ${data.response_time_ms} ms`;
        } else {
            checks.http.result.textContent = data.error;
        }

    } catch (error) {
        checks.http.status.textContent = "Error";
        checks.http.status.className = "status failure";
        checks.http.result.textContent = error.message;
    } finally {
        finishCheck("http");
    }
}


async function runPingCheck() {
    const host = document.getElementById("pingHost").value.trim();

    if (!host) {
        showError("Please enter a ping host.");
        return;
    }

    clearError();
    setLoading("ping");

    try {
        const response = await fetch(
            `/api/ping?host=${encodeURIComponent(host)}`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Ping check failed.");
        }

        setStatus("ping", data.success);

        if (data.success) {
            checks.ping.result.textContent =
                `${data.packet_loss_percent ?? 0}% packet loss`;
        } else {
            checks.ping.result.textContent = data.error;
        }

    } catch (error) {
        checks.ping.status.textContent = "Error";
        checks.ping.status.className = "status failure";
        checks.ping.result.textContent = error.message;
    } finally {
        finishCheck("ping");
    }
}


function setFullDiagnosticLoading() {
    Object.values(checks).forEach((check) => {
        check.status.textContent = "Testing...";
        check.status.className = "status loading";
        check.result.textContent = "Running...";
    });

    overallStatus.textContent = "Running...";
    overallStatus.className = "overall-status loading";

    runButton.disabled = true;
    runButton.textContent = "Running...";
}


function updateFullDiagnosticResults(data) {

    setStatus("dns", data.dns.success);
    checks.dns.result.textContent = data.dns.success
        ? `${data.dns.response_time_ms} ms • ${data.dns.addresses.length} address(es)`
        : data.dns.error;

    setStatus("tcp", data.tcp.success);
    checks.tcp.result.textContent = data.tcp.success
        ? `${data.tcp.response_time_ms} ms`
        : data.tcp.error;

    setStatus("http", data.http.success);
    checks.http.result.textContent = data.http.success
        ? `${data.http.status_code} • ${data.http.response_time_ms} ms`
        : data.http.error;

    setStatus("ping", data.ping.success);
    checks.ping.result.textContent = data.ping.success
        ? `${data.ping.packet_loss_percent ?? 0}% packet loss`
        : data.ping.error;

    overallStatus.textContent = data.overall_status;
    overallStatus.className =
        `overall-status ${data.overall_status.toLowerCase()}`;

    diagnosticTime.textContent =
        `Last checked: ${new Date(data.timestamp).toLocaleString()}`;
}


async function runFullDiagnostics() {
    clearError();
    setFullDiagnosticLoading();

    try {
        const response = await fetch("/api/diagnostics");

        if (!response.ok) {
            throw new Error("Diagnostic request failed.");
        }

        const data = await response.json();

        hostnameElement.textContent = data.local.hostname;
        localIpElement.textContent = data.local.local_ip;
        operatingSystemElement.textContent = data.local.os;

        updateFullDiagnosticResults(data);

    } catch (error) {
        overallStatus.textContent = "Error";
        overallStatus.className = "overall-status failure";
        showError(`Unable to complete diagnostics: ${error.message}`);
    } finally {
        runButton.disabled = false;
        runButton.textContent = "Run Full Diagnostics";

        Object.values(checks).forEach((check) => {
            check.button.disabled = false;
        });
    }
}


document
    .getElementById("dnsButton")
    .addEventListener("click", runDnsCheck);

document
    .getElementById("tcpButton")
    .addEventListener("click", runTcpCheck);

document
    .getElementById("httpButton")
    .addEventListener("click", runHttpCheck);

document
    .getElementById("pingButton")
    .addEventListener("click", runPingCheck);

runButton.addEventListener("click", runFullDiagnostics);

loadLocalInfo();