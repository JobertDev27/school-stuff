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


print("[1] Network Interface")

res = run(["powershell", "-NoProfile", "-Command",
           "Get-NetAdapter | Select-Object Name, Status | ConvertTo-Csv -NoTypeInformation"])

interface = None

if res is None or res.returncode != 0:
    check("Interface status", "FAIL", "Unable to run PowerShell command")
else:
    adapters = []
    for line in res.stdout.splitlines()[1:]:
        fields = re.findall(r'"((?:[^"]|"")*)"', line)
        if len(fields) >= 2:
            adapters.append([fields[0].replace('""', '"'), fields[1]])

    route = run(["powershell", "-NoProfile", "-Command",
                 "(Get-NetRoute -DestinationPrefix '0.0.0.0/0' -ErrorAction SilentlyContinue | Sort-Object RouteMetric | Select-Object -First 1).InterfaceAlias"])

    if route and route.returncode == 0:
        interface = route.stdout.strip() or None

    if not interface:
        for fields in adapters:
            if fields[1] == "Up":
                interface = fields[0]
                break

    if interface:
        state = next(
            (fields[1] for fields in adapters
             if fields[0] == interface),
            "UNKNOWN"
        )

        if state == "Up":
            check("Interface status", "PASS", interface + " is UP")
        elif state == "Disabled":
            check("Interface status", "FAIL", interface + " is DOWN")
        else:
            check("Interface status", "WARNING",
                  interface + " state is " + state)
    else:
        check("Interface status", "FAIL", "No active interface found")


print("\n[2] IP Address")

has_ip = False

if interface:
    res = run(["powershell", "-NoProfile", "-Command",
               f"Get-NetIPAddress -InterfaceAlias '{interface.replace(chr(39), chr(39)*2)}' -ErrorAction SilentlyContinue | Select-Object IPAddress, AddressFamily | ConvertTo-Csv -NoTypeInformation"])

    if res is not None and res.returncode == 0:
        for line in res.stdout.splitlines()[1:]:
            fields = re.findall(r'"((?:[^"]|"")*)"', line)
            if len(fields) >= 2:
                ip = fields[0]
                if fields[1] == "IPv4":
                    if not ip.startswith("127.") and not ip.startswith("169.254."):
                        has_ip = True
                elif fields[1] == "IPv6":
                    if ip != "::1" and not ip.lower().startswith("fe80:"):
                        has_ip = True

if has_ip:
    check("IP assignment", "PASS", "Address assigned")
elif interface:
    check("IP assignment", "FAIL", "No usable IP address found")
else:
    check("IP assignment", "WARNING", "No interface to check")


print("\n[3] Default Gateway")

gateway = None
route = run(["powershell", "-NoProfile", "-Command",
             "(Get-NetRoute -DestinationPrefix '0.0.0.0/0' -ErrorAction SilentlyContinue | Sort-Object RouteMetric | Select-Object -First 1).NextHop"])

if route is not None and route.returncode == 0:
    gateway = route.stdout.strip() or None

if gateway and gateway != "0.0.0.0":
    check("Default gateway", "PASS", gateway)
else:
    gateway = None
    check("Default gateway", "FAIL", "No default route found")


print("\n[4] Gateway Connectivity")

if gateway:
    res = run(["ping", "-n", "2", "-w", "2000", gateway])

    if res is not None and res.returncode == 0:
        check("Gateway ping", "PASS", "Router responds")
    elif res is None:
        check("Gateway ping", "WARNING", "Ping unavailable or timed out")
    else:
        check("Gateway ping", "FAIL", "No replies from gateway")
else:
    check("Gateway ping", "WARNING", "Skipped: no gateway")


print("\n[5] Internet Connectivity")

res = run(["ping", "-n", "2", "-w", "2000", "1.1.1.1"])

if res is not None and res.returncode == 0:
    check("Internet ping", "PASS", "1.1.1.1 responds")
elif res is None:
    check("Internet ping", "WARNING", "Ping unavailable or timed out")
else:
    check("Internet ping", "FAIL", "No replies from external IP")


print("\n[6] DNS Resolution")

res = run(["powershell", "-NoProfile", "-Command",
           "Resolve-DnsName example.com -ErrorAction Stop | Select-Object -First 1 -ExpandProperty Name"])

if res is not None and res.returncode == 0 and res.stdout.strip():
    check("DNS lookup", "PASS", "example.com resolved")
elif res is None:
    check("DNS lookup", "WARNING", "Command unavailable or timed out")
else:
    check("DNS lookup", "FAIL", "Hostname resolution failed")


print("\n[7] HTTPS Connectivity")

res = run(["powershell", "-NoProfile", "-Command",
           "$ProgressPreference='SilentlyContinue'; try { $r = Invoke-WebRequest -Uri 'https://example.com' -Method Head -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop; Write-Output ('HTTP/' + [int]$r.StatusCode); exit 0 } catch { if ($_.Exception.Response) { Write-Output ('HTTP/' + [int]$_.Exception.Response.StatusCode); exit 0 } else { exit 1 } }"])

if res is None:
    check("HTTPS request", "WARNING", "PowerShell unavailable or timed out")
elif res.returncode == 0 and res.stdout.startswith("HTTP/"):
    check("HTTPS request", "PASS", "Received HTTP response")
else:
    check("HTTPS request", "FAIL", "HTTPS request failed")


print("\n========== SUMMARY ==========")
print(f"Passed:   {results['PASS']}")
print(f"Warnings: {results['WARNING']}")
print(f"Failed:   {results['FAIL']}")
print("==============================")
