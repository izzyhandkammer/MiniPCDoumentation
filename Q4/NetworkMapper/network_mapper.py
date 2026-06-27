import nmap
import requests
import time
import re
import subprocess

scanner = nmap.PortScanner()

SUBNET = ""  # Specify the target network range
KNOWN_HOSTS = "known_macs.txt"

# XDR API Credentials
XDR_URL = "https://izzylab.xdr.us.paloaltonetworks.com" 
API_KEY = "YOUR_API_KEY"
API_KEY_ID = "1"

def load_known_hosts():
    """Load known hosts from a file."""
    try:
        with open(KNOWN_HOSTS, 'r') as file:
            return {line.strip() for line in file}
    except FileNotFoundError:
        return set()


def append_new_mac(mac_address):
    """Append a new MAC address to the known hosts file."""
    with open(KNOWN_HOSTS, 'a') as file:
        file.write(f"\n{mac_address.lower()}")

def run_scan():
    """run a sudo nmap scan on the subnet and parses IPs and MAC addresses from the raw text output"""
    print (f"[*] Starting network scan on {SUBNET}...")
    try:
        result = subprocess.run(
            ['sudo', 'nmap', '-sn', SUBNET],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running nmap: {e}")
        return []

    scan_output = result.stdout
    devices_found = []

    host_blocks = scan_output.split("Nmap scan report for ")

    for block in host_blocks[1:]:  # Skip the first split as it will be empty
        lines = block.splitlines()
        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', lines[0])

# these .group(1) calls could be an issue
        if ip_match:
            ip_address = ip_match.group(1)
            mac_address = None

            for line in lines:
                if "MAC Address" in line:
                    mac_match = re.search(r'MAC Address: ([0-9A-Fa-f:]+)', line)
                    if mac_match:
                        mac_address = mac_match.group(1).lower()
                        break
            if mac_address:
                devices_found.append({"ip": ip_address, "mac": mac_address})
    return devices_found


def send_to_xdr(ip, mac):
    """
        format and posts a parsed alert to the XDR API
        the documentation for formatting and posting a parsed alert to the XDR API can be found here: 
        https://docs-cortex.paloaltonetworks.com/r/Cortex-XDR-REST-API/Insert-Parsed-Alerts
    """
    endpoint = f"{XDR_URL}/public_api/v1/alerts/insert_parsed_alerts"

    headers = {
        "Content-Type": "application/json",
        "x-xdr-auth-id": API_KEY_ID,
        "Authorization": API_KEY
    }

    payload = {
        "request_data": {
            "alerts": [
                {
                    "product": "Home Network Mapper",
                    "vendor": "Raspberry Pi",
                    "severity": "Medium",
                    "alert_name": "Rougue MAC Address Detected",
                    "alert_description": f"An unverified device with MAC Address [{mac}] entered the network using IP [{ip}].",
                    "action_status": "Reported",
                    "event_timestamp": int(time.time() * 1000),
                }
            ]
        }
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        if response.status_code == 200:
            print(f"[+] Alert sent to XDR for MAC: {mac}, IP: {ip}")
        else:
            print(f"[-] Failed to send alert to XDR. Status Code: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"[-] Error sending alert to XDR: {e}")

def main():
    known_hosts = load_known_hosts()
    devices_found = run_scan()

    print(f"[*] Found {len(devices_found)} total alive devices.")

    for device in devices_found:
        ip = device["ip"]
        mac = device["mac"]

        if mac not in known_hosts:
            print(f"[!] New device detected: IP: {ip}, MAC: {mac}")
            append_new_mac(mac)
            send_to_xdr(ip, mac)
        else:
            print(f"[+] Known device: IP: {ip}, MAC: {mac}")

if __name__ == "__main__":
    main()