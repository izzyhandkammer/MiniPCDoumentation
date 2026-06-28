# Network Mapper on Kali Linux

This project scans a local subnet with `nmap`, detects new MAC addresses, and can send alerts to a Cortex XDR endpoint. The instructions below are written for Kali Linux, but the script should work on any Debian-based Linux distro with Python and `nmap` installed.

## What you need

- A Kali Linux machine that can stay on while scanning the network
- `nmap` installed and usable from the command line
- Python 3.11+ with `pip`
- A `.env` file in the project directory with your network range and XDR credentials

## Setup

1. Open a terminal on Kali.
2. Update packages:
   - `sudo apt update && sudo apt upgrade -y`
3. Install Python and dependencies:
   - `sudo apt install python3 python3-pip python3-venv -y`
4. Install `nmap` if it is not already installed:
   - `sudo apt install nmap -y`
5. Clone or copy this repo into a working folder.
6. Change into the project directory:
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

- `SUBNET` should match your target network range.
- `XDR_URL`, `API_KEY`, and `API_KEY_ID` are used only if you want the script to post alerts to Cortex XDR.

## Run the scanner

1. Make sure `.env` is present in the same folder as `network_mapper.py`.
2. Run the script:
   - `python3 network_mapper.py`
3. The script will scan the subnet and print discovered devices.

## Notes

- The script expects a `known_macs.txt` file in the project folder. If it does not exist, it will start with an empty known list.
- Add the currently connected devices to `known_macs.txt` first if you want to create a baseline and only alert on unknown MAC addresses.
- If the scan fails with a missing subnet error, double-check that `SUBNET` is set in `.env`.

## Kali-specific tips

- Run the scanner as a user with `sudo` access since `nmap` may require privileges for network discovery.
- If you are using Kali in a VM, confirm the VM network adapter is bridged or on the same subnet as the devices you want to scan.

## Optional improvements

- Use `crontab` to run the script periodically.
- Store the baseline list in `known_macs.txt` and share it with your team so everyone is using the same trusted devices.
