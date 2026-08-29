const runButton = document.getElementById("runDiagnostics");

const hostnameElement = document.getElementById("hostname");
const localIpElement = document.getElementById("localIp");
const operatingSystemElement = document.getElementById("operatingSystem");

const errorMessage = document.getElementById("errorMessage");

const checks = {
    internet: {
        status: document.getElementById("internetStatus"),
        result: document.getElementById("internetResult"),
    },
    dns: {
        status: document.getElementById("dnsStatus"),
        result: document.getElementById("dnsResult"),
    },
    tcp: {
        status: document.getElementById("tcpStatus"),
        result: document.getElementById("tcpResult"),
    },
    http: {
        status: document.getElementById("httpStatus"),
        result: document.getElementById("httpResult"),
    },
    ping: {
        status: document.getElementById("pingStatus"),
        result: document.getElementById("pingResult"),
    },
};

const overallStatus = document.getElementById("overallStatus");
const diagnosticTime = document.getElementById("diagnosticTime");


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
    } catch (error) {
        hostnameElement.textContent = "Unavailable";
        localIpElement.textContent = "Unavailable";
        operatingSystemElement.textContent = "Unavailable";
    }
}


function setCheckResult(name, success, resultText) {
    const check = checks[name];

    check.status.textContent = success ? "Healthy" : "Failed";
    check.status.className = `status ${success ? "success" : "failure"}`;
    check.result.textContent = resultText;
}


function setLoadingState() {
    Object.values(checks).forEach((check) => {
        check.status.textContent = "Testing...";
        check.status.className = "status loading";
        check.result.textContent = "Running diagnostic...";
    });

    overallStatus.textContent = "Running...";
    overallStatus.className = "overall-status loading";

    errorMessage.classList.add("hidden");
}


function formatCheckResults(data) {
    setCheckResult(
        "internet",
        data.internet.success,
        data.internet.success
            ? `${data.internet.latency_ms} ms`
            : data.internet.error
    );

    setCheckResult(
        "dns",
        data.dns.success,
        data.dns.success
            ? `${data.dns.response_time_ms} ms • ${data.dns.addresses.length} address(es)`
            : data.dns.error
    );

    setCheckResult(
        "tcp",
        data.tcp.success,
        data.tcp.success
            ? `${data.tcp.response_time_ms} ms`
            : data.tcp.error
    );

    setCheckResult(
        "http",
        data.http.success,
        data.http.success
            ? `${data.http.status_code} • ${data.http.response_time_ms} ms`
            : data.http.error
    );

    setCheckResult(
        "ping",
        data.ping.success,
        data.ping.success
            ? `${data.ping.packet_loss_percent ?? 0}% packet loss`
            : data.ping.error
    );
}


async function runDiagnostics() {
    setLoadingState();

    runButton.disabled = true;
    runButton.textContent = "Running...";

    try {
        const response = await fetch("/api/diagnostics");

        if (!response.ok) {
            throw new Error("Diagnostic request failed.");
        }

        const data = await response.json();

        hostnameElement.textContent = data.local.hostname;
        localIpElement.textContent = data.local.local_ip;
        operatingSystemElement.textContent = data.local.os;

        formatCheckResults(data);

        overallStatus.textContent = data.overall_status;
        overallStatus.className =
            `overall-status ${data.overall_status.toLowerCase()}`;

        diagnosticTime.textContent =
            `Last checked: ${new Date(data.timestamp).toLocaleString()}`;

    } catch (error) {
        errorMessage.textContent =
            `Unable to complete diagnostics: ${error.message}`;

        errorMessage.classList.remove("hidden");

        overallStatus.textContent = "Error";
        overallStatus.className = "overall-status failure";
    } finally {
        runButton.disabled = false;
        runButton.textContent = "Run Full Diagnostics";
    }
}


runButton.addEventListener("click", runDiagnostics);

loadLocalInfo();