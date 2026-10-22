import subprocess
import re

print("========== TROUBLE ME 1.0 ==========\n")

results = {"PASS": 0, "WARNING": 0, "FAIL": 0}


def check(name, status, message=""):
    results[status] += 1
    print(f"{name:<25} {status:<8} {message}")


def run(command):
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=5
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


# 1. Check network interfaces
print("[1] Network Interface")

res = run(["ip", "-br", "link"])
interface = None

if res is None or res.returncode != 0:
    check("Interface status", "FAIL", "Unable to run ip command")
else:
    interfaces = [line.split() for line in res.stdout.splitlines()]

    # Prefer the interface used by the default route
    route = run(["ip", "route", "show", "default"])
    if route:
        match = re.search(r"\bdev\s+(\S+)", route.stdout)
        if match:
            interface = match.group(1)

    # If there is no default route, find an interface that is UP
    if not interface:
        for fields in interfaces:
            if fields[0] != "lo" and fields[1] == "UP":
                interface = fields[0]
                break

    if interface:
        state = next(
            (fields[1] for fields in interfaces
             if fields[0] == interface),
            "UNKNOWN"
        )

        if state == "UP":
            check("Interface status", "PASS", interface + " is UP")
        elif state == "DOWN":
            check("Interface status", "FAIL", interface + " is DOWN")
        else:
            check("Interface status", "WARNING",
                  interface + " state is " + state)
    else:
        check("Interface status", "FAIL", "No active interface found")


# 2. Check IP assignment
print("\n[2] IP Address")

has_ip = False

if interface:
    res = run(["ip", "-o", "addr", "show", "dev", interface])

    if res is not None and res.returncode == 0:
        for line in res.stdout.splitlines():
            fields = line.split()

            if "inet" in fields:
                ip = fields[fields.index("inet") + 1].split("/")[0]
                if not ip.startswith("127.") and not ip.startswith("169.254."):
                    has_ip = True

            if "inet6" in fields:
                ip = fields[fields.index("inet6") + 1].split("/")[0]
                if ip != "::1" and not ip.startswith("fe80:"):
                    has_ip = True

if has_ip:
    check("IP assignment", "PASS", "Address assigned")
elif interface:
    check("IP assignment", "FAIL", "No usable IP address found")
else:
    check("IP assignment", "WARNING", "No interface to check")


# 3. Check default gateway
print("\n[3] Default Gateway")

gateway = None
route = run(["ip", "route", "show", "default"])

if route is not None and route.returncode == 0:
    match = re.search(r"\bdefault via (\S+)", route.stdout)
    if match:
        gateway = match.group(1)

if gateway:
    check("Default gateway", "PASS", gateway)
else:
    check("Default gateway", "FAIL", "No default route found")


# 4. Check gateway connectivity
print("\n[4] Gateway Connectivity")

if gateway:
    res = run(["ping", "-c", "2", "-W", "2", gateway])

    if res is not None and res.returncode == 0:
        check("Gateway ping", "PASS", "Router responds")
    elif res is None:
        check("Gateway ping", "WARNING", "Ping unavailable or timed out")
    else:
        check("Gateway ping", "FAIL", "No replies from gateway")
else:
    check("Gateway ping", "WARNING", "Skipped: no gateway")


# 5. Check internet connectivity
print("\n[5] Internet Connectivity")

res = run(["ping", "-c", "2", "-W", "2", "1.1.1.1"])

if res is not None and res.returncode == 0:
    check("Internet ping", "PASS", "1.1.1.1 responds")
elif res is None:
    check("Internet ping", "WARNING", "Ping unavailable or timed out")
else:
    check("Internet ping", "FAIL", "No replies from external IP")


# 6. Check DNS resolution
print("\n[6] DNS Resolution")

res = run(["getent", "hosts", "example.com"])

if res is not None and res.returncode == 0 and res.stdout.strip():
    check("DNS lookup", "PASS", "example.com resolved")
elif res is None:
    check("DNS lookup", "WARNING", "Command unavailable or timed out")
else:
    check("DNS lookup", "FAIL", "Hostname resolution failed")


# 7. Check HTTPS connectivity
print("\n[7] HTTPS Connectivity")

res = run(["curl", "-I", "-sS", "--max-time", "5",
           "https://example.com"])

if res is None:
    check("HTTPS request", "WARNING", "curl unavailable or timed out")
elif res.returncode == 0 and res.stdout.startswith("HTTP/"):
    check("HTTPS request", "PASS", "Received HTTP response")
else:
    check("HTTPS request", "FAIL", "HTTPS request failed")


# Summary
print("\n========== SUMMARY ==========")
print(f"Passed:   {results['PASS']}")
print(f"Warnings: {results['WARNING']}")
print(f"Failed:   {results['FAIL']}")
print("==============================")
