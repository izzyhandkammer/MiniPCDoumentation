import nmap
import requests
import time
import socket
import os
from pathlib import Path
from dotenv import load_dotenv

scanner = nmap.PortScanner()

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

if not ENV_FILE.exists():
    print(f"[!] Warning: .env file not found at {ENV_FILE}")

load_dotenv(ENV_FILE)

SUBNET = os.getenv("SUBNET")  # Wifi network range to scan for new devices
if not SUBNET:
    raise SystemExit("[!] Missing SUBNET value in .env. Please set SUBNET.")

MAC_VENDOR_API = "https://api.macvendors.com/{}"
_last_vendor_lookup = 0.0

KNOWN_HOSTS = BASE_DIR / "known_macs.txt"

# XDR API Credentials
XDR_URL = os.getenv("XDR_URL")
API_KEY = os.getenv("API_KEY")
API_KEY_ID = os.getenv("API_KEY_ID")
TEST = os.getenv("TEST")


def load_known_hosts():
    """Load known hosts from a file."""
    try:
        with open(KNOWN_HOSTS, 'r', encoding="utf-8") as file:
            return {line.strip() for line in file}
    except FileNotFoundError:
        return set()


def append_new_mac(mac_address):
    """Append a new MAC address to the known hosts file."""
    with open(KNOWN_HOSTS, 'a', encoding="utf-8") as file:
        file.write(f"\n{mac_address.lower()}")


def discover_devices():
    """Fast ping sweep of the subnet; returns live hosts with MAC, nmap's offline vendor guess, and hostname."""
    print(f"[*] Starting discovery scan on {SUBNET}...")
    try:
        scanner.scan(hosts=SUBNET, arguments="-sn")
    except nmap.PortScannerError as e:
        print(f"[-] Error running nmap discovery scan: {e}")
        return []

    devices_found = []
    for host in scanner.all_hosts():
        if scanner[host].state() != "up":
            continue

        mac_address = scanner[host]["addresses"].get("mac")
        if not mac_address:
            continue  # No MAC visible (ARP unavailable) means it's not on our local segment

        mac_address = mac_address.lower()
        vendor_dict = scanner[host].get("vendor", {})
        vendor = next(iter(vendor_dict.values()), None)
        hostname = scanner[host].hostname() or None

        devices_found.append({
            "ip": host,
            "mac": mac_address,
            "vendor": vendor,
            "hostname": hostname,
        })
    return devices_found


def deep_scan_host(ip):
    """OS fingerprint + service/version detection + default NSE scripts against a single new device."""
    print(f"[*] Running deep scan on {ip}...")
    try:
        scanner.scan(hosts=ip, arguments="-O -sV -sC -T4 --osscan-guess")
    except nmap.PortScannerError as e:
        print(f"[-] Error running deep scan on {ip}: {e}")
        return {"os_guess": "Unknown", "open_ports": []}

    if ip not in scanner.all_hosts():
        return {"os_guess": "Unknown", "open_ports": []}

    host_info = scanner[ip]

    os_guess = "Unknown"
    osmatches = host_info.get("osmatch")
    if osmatches:
        best = osmatches[0]
        os_guess = f"{best['name']} ({best['accuracy']}% confidence)"

    open_ports = []
    for proto in ("tcp", "udp"):
        for port, port_info in host_info.get(proto, {}).items():
            if port_info.get("state") != "open":
                continue
            descriptor = f"{port}/{proto} {port_info.get('name', 'unknown')}"
            extra = " ".join(filter(None, [port_info.get("product"), port_info.get("version")]))
            if extra:
                descriptor += f" ({extra})"
            open_ports.append(descriptor)

    return {"os_guess": os_guess, "open_ports": open_ports}


def resolve_hostname(ip_address):
    """Fallback reverse DNS lookup when nmap didn't already resolve a hostname."""
    try:
        return socket.gethostbyaddr(ip_address)[0]
    except (socket.herror, socket.gaierror, OSError):
        return "Unknown"


def get_mac_vendor(mac_address):
    """Fallback OUI vendor lookup via api.macvendors.com, used when nmap's local database has no match."""
    global _last_vendor_lookup

    # Free tier is rate-limited to ~1 request/sec; throttle to stay under it.
    elapsed = time.time() - _last_vendor_lookup
    if elapsed < 1:
        time.sleep(1 - elapsed)

    try:
        response = requests.get(MAC_VENDOR_API.format(mac_address), timeout=5)
        _last_vendor_lookup = time.time()
        if response.status_code == 200:
            return response.text.strip()
        if response.status_code == 404:
            return "Unknown"
        print(f"[-] MAC vendor lookup failed for {mac_address}: {response.status_code}")
        return "Unknown"
    except requests.RequestException as e:
        print(f"[-] Error looking up MAC vendor for {mac_address}: {e}")
        return "Unknown"


def send_to_xdr(ip, mac, hostname="Unknown", mac_vendor="Unknown", os_guess="Unknown", open_ports=None):
    """
        format and posts a parsed alert to the XDR API
        the documentation for formatting and posting a parsed alert to the XDR API can be found here:
        https://docs-cortex.paloaltonetworks.com/r/Cortex-XDR-REST-API/Insert-Parsed-Alerts
    """
    endpoint = f"{XDR_URL}/public_api/v1/alerts/insert_parsed_alerts"

    headers = {
        "Authorization": API_KEY,
        "x-xdr-auth-id": API_KEY_ID,
        "Accept-Encoding": "gzip",
        "content-type": "application/json"
    }

    ports_summary = "; ".join(open_ports) if open_ports else "No open ports detected"

    payload = {
        "request_data": {
            "alerts": [
                {
                    "product": "Home Network Mapper",
                    "vendor": "Raspberry Pi",
                    "local_ip": ip,
                    "local_port": 8888,
                    "event_timestamp": int(time.time() * 1000),
                    "severity": "Medium",
                    "alert_name": "Rougue MAC Address Detected",
                    "alert_description": (
                        f"An unverified device with MAC Address [{mac}] ({mac_vendor}) "
                        f"and hostname [{hostname}] entered the network using IP [{ip}]. "
                        f"OS guess: {os_guess}. Open ports: {ports_summary}."
                    ),
                    "action_status": "Reported",
                    "remote_ip": "0.0.0.0",
                    "remote_port": 8888
                }
            ]
        }
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get("reply") is True:
                print(f"[+] Alert successfully processed by XDR for MAC: {mac}")
            else:
                print(f"[-] Gateway accepted request, but backend failed: {response.text}")
        else:
            print(f"[-] Failed to send alert to XDR. Status Code: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"[-] Error sending alert to XDR: {e}")

def main():
    known_hosts = load_known_hosts()
    devices_found = discover_devices()

    print(f"[*] Found {len(devices_found)} total alive devices.")

    for device in devices_found:
        ip = device["ip"]
        mac = device["mac"]
        hostname = device["hostname"] or resolve_hostname(ip)

        if mac not in known_hosts:
            mac_vendor = device["vendor"] or get_mac_vendor(mac)
            deep_info = deep_scan_host(ip)
            os_guess = deep_info["os_guess"]
            open_ports = deep_info["open_ports"]

            print(
                f"[!] New device detected: IP: {ip}, MAC: {mac} ({mac_vendor}), "
                f"Hostname: {hostname}, OS: {os_guess}, Open ports: {', '.join(open_ports) or 'none'}"
            )
            append_new_mac(mac)
            send_to_xdr(
                ip, mac,
                hostname=hostname,
                mac_vendor=mac_vendor,
                os_guess=os_guess,
                open_ports=open_ports,
            )
        else:
            print(f"[+] Known device: IP: {ip}, MAC: {mac}, Hostname: {hostname}")

if __name__ == "__main__":
    main()
