# Network Mapper

This project scans your WiFi subnet with `nmap`, detects new MAC addresses joining the network, and enriches each new device before alerting Cortex XDR: MAC vendor (nmap's offline OUI database, falling back to api.macvendors.com), hostname (reverse DNS), OS fingerprint, and open ports/services (via a targeted `-O -sV -sC` scan). It's designed to run on a Raspberry Pi Zero W connected directly to the WiFi network it's monitoring, so ARP-based host discovery works without needing to cross firewall zone boundaries.

## What you need

- A Raspberry Pi Zero W, flashed with Raspberry Pi OS Lite, connected to the WiFi SSID you want to monitor (not a wired trust-network connection)
- A stable 5V/1A+ power supply — the Zero W is sensitive to undervoltage, which can cause silent WiFi drops
- A DHCP reservation for the Pi on your WiFi network/AP so its own IP doesn't shift
- `nmap` installed and usable from the command line
- Python 3.11+ with `pip`
- A `.env` file in the project directory with your network range and XDR credentials

## Setup

1. Flash Raspberry Pi OS Lite (32-bit, ARMv6-compatible) to the SD card and configure it to join your WiFi SSID during first boot.
2. SSH into the Pi.
3. Update packages:
   - `sudo apt update && sudo apt upgrade -y`
4. Install Python and dependencies:
   - `sudo apt install python3 python3-pip python3-venv -y`
5. Install `nmap`:
   - `sudo apt install nmap -y`
6. Clone or copy this repo into a working folder.
7. Change into the project directory:
   - `cd /path/to/NetworkMapper`

## Python environment

1. Create a virtual environment (recommended):
   - `python3 -m venv .venv`
2. Activate it:
   - `source .venv/bin/activate`
3. Install the required Python packages:
   - `pip install python-dotenv requests python-nmap`

## Configure `.env`

Create a `.env` file in the project root with these values:

```dotenv
XDR_URL=https://your-url.xdr.us.paloaltonetworks.com
API_KEY=your_api_key_here
API_KEY_ID=your_api_key_id_here
SUBNET= your.subnet
TEST=true
```

- `SUBNET` should be your **WiFi network's** CIDR range (e.g. `192.168.20.0/24`) — find it via your Palo Alto's interface config for the WiFi zone, its DHCP server pool, or by running `ip addr` on any device already connected to that WiFi.
- `XDR_URL`, `API_KEY`, and `API_KEY_ID` are used only if you want the script to post alerts to Cortex XDR.

## Run the scanner

1. Make sure `.env` is present in the same folder as `network_mapper.py`.
2. Run the script **as root** (required for ARP-based discovery and OS fingerprinting):
   - `sudo .venv/bin/python3 network_mapper.py`
3. The script will scan the subnet, then for any brand-new MAC it finds, run a deeper scan and print hostname, MAC vendor, OS guess, and open ports/services.

## Detecting new devices quickly

The script itself runs a single scan-and-exit pass, so to catch devices "as they join" the WiFi network, schedule it to run every 1-2 minutes with **root's** `crontab` (the deep OS/service scan needs raw-socket privileges, so the cron job must run as root, not the `pi` user):

```bash
sudo crontab -e
```

Add a line like:

```
*/2 * * * * cd /path/to/NetworkMapper && /path/to/.venv/bin/python3 network_mapper.py >> scan.log 2>&1
```

This re-scans the WiFi subnet every 2 minutes; any MAC not already in `known_macs.txt` is treated as new, deep-scanned, and alerted to XDR. Since the Pi lives on the WiFi subnet itself, nmap can use real ARP discovery here rather than routed ICMP probes, so results are more complete than scanning from a device on a different subnet/zone.

Because the deep scan (`-O -sV -sC`) runs a full port scan against each new device, expect it to take anywhere from several seconds to a couple of minutes per new device — that's fine for a low-churn home network, since it only fires on genuinely new MACs, not on every sweep.

## Enrichment

- **MAC vendor**: nmap's bundled offline OUI database is checked first (works even with no internet access); if nmap doesn't recognize the OUI, the free `api.macvendors.com` API is used as a fallback, throttled to ~1 request/second. Locally-administered/randomized MACs (common on phones by default) won't resolve either way.
- **Hostname**: taken from nmap's reverse-DNS resolution when available, with a Python `socket.gethostbyaddr` fallback. Devices with no PTR record and no NetBIOS/mDNS response will show as `Unknown`.
- **OS fingerprint**: nmap's `-O` OS detection, run only against new devices. Accuracy varies — some devices (especially phones/IoT) won't fingerprint cleanly and will show as `Unknown`.
- **Open ports/services**: nmap's `-sV -sC` service/version detection plus default NSE scripts, run only against new devices. Lists each open port with its service name and, when detected, product/version.

## Notes

- The script expects a `known_macs.txt` file in the project folder. If it does not exist, it will start with an empty known list.
- Add the currently connected devices to `known_macs.txt` first if you want to create a baseline and only alert on unknown MAC addresses.
- If the scan fails with a missing subnet error, double-check that `SUBNET` is set in `.env`.
- The script must run as root — ARP-based host discovery and `-O` OS detection both require raw-socket privileges nmap can't get otherwise. Without root, OS detection will silently return `Unknown` for every device.
- Since the Pi sits on the WiFi network being monitored (not the trust network), keep the `.env` XDR credentials on the Pi's filesystem only and avoid exposing SSH to that network beyond what you need.

## Optional improvements

- Store the baseline list in `known_macs.txt` and share it with your team so everyone is using the same trusted devices.
