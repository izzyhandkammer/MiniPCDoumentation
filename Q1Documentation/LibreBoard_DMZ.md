# DMZ Host Deployment: Libre Computer La Frite

This document details the complete process for configuring the Libre Computer La Frite SBC as the dedicated $\text{DMZ}$ host for my KSO lab. This includes the operating system installation, network configuration, and enabling remote access.
## 1. OS Flashing and Initial Access (Armbian CLI)
### 1.1. Prepare the Installation Media
The $\text{La Frite}$ requires a specific procedure to install the OS (Armbian Server, a minimal CLI distribution).
Flash Tool: I used Raspberry Pi Imager to write the Armbian image to a high-speed USB drive (or microSD card).
To avoid file system errors, I explicitly DID NOT use any OS Customization settings within the Imager.

### 1.2. Initial Boot and User Setup
1. Initial Connection: I connected the USB drive, an $\text{HDMI}$ monitor, and a keyboard to the La Frite.
2. Power On: I powered on the La Frite and waited for the Armbian system to boot to the console login prompt.
3. Default Login: I logged in using the default credentials [root, 1234].
4. Security Setup: The system prompted me to set a root password and then create a standard non-root user.

## Cabling and Physical Interface Notes
Since the La Frite is a physical component, proper cabling was essential for the $\text{DMZ}$ segment to function.
* **PA-440 Connection:** The $\text{end0}$ interface of the $\text{La Frite}$ was connected directly to the $\text{ethernet1/3}$ port on the PA-440. You could also use a dedicated switch port leading only to $\text{e1/3}$).
* **Segment Isolation:** It was critical to ensure the La Frite was not accidentally plugged into the $\text{Trust}$ zone switch or the T-Mobile router, as this would completely bypass the firewall segmentation. I confirmed the $\text{172.16.1.1/24}$ subnet was exclusively handled by the  $\text{e1/3}$ interface.
* **Link Status:** The link status changes based on hardware and configuration:
   * Physical Link (Cable Connected): The LED status on both the La Frite and the $\text{ethernet1/3}$ port on the PA-440 will show a constant color (GREEN or YELLOW) immediately upon connection and power-on. This confirms the Layer 1 connection is good.
   * Protocol Link (Before Config): The LED color will not change before configuring Netplan, as the link status is governed by hardware. The operational status is Down/Unready because the host has no valid IP address.
   * Protocol Link (After Config): After running sudo netplan apply, the status will change to Up/Ready, and the LED will start flashing intermittently, indicating Layer 2/3 traffic is active (e.g., ARP requests, DNS lookups).

## 2. Configure Static IP (Netplan)
1. Edit Netplan File: Access the network configuration file: `sudo nano /etc/netplan/01-netcfg.yaml`
2. Apply Configuration: Ensure the file uses the correct interface name and settings:
```
network:
   version: 2
   renderer: NetworkManager
   ethernets:
    end0:
      dhcp4: no
      addresses:
        - 172.16.1.100/24  # Static IP for the DMZ host
      routes:
        - to: default
          via: 172.16.1.1  # DMZ Gateway
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```
  Note: be sure to use correct YAML syntax, using spaces as opposed to Tab indentations. I also had issues with the config sticking as I wrote out `eth0` as opposed to `end0`.
  
3. Write out the file with `Ctrl + O`, enter, and exit with `Ctrl + X`.
4. Apply Netplan Changes:
```
sudo netplan apply
ip a                                  # Verify 172.16.1.100/24 is active
ping 8.8.8.8                          # Verify Internet access through firewall
```
## 3.Enable Remote Access (SSH)
Since I had to keep switching HDMI and Keyboard inputs between my PC and the LibreBoard, I enabled SSH to allow for headless operation from my PC.
1. Install SSH server:
`sudo apt install openssh-server -y`
2. Start Service:
`sudo systemctl start ssh`
3. Enable on boot:
`sudo systemctl enable ssh`
4. Remote Access Test: Now disconnect the HDMI and keyboard from the LibreBoard and connected to my PC. Open a new terminal window and input:
`ssh izzy@172.16.1.100`

## 4. Lab Testing and Traffic Simulation
To fully test the App-ID and Content-ID features, I installed several key services on the DMZ host.
| Feature Test      | LibreBoard Command (Preparation)             | Purpose in Lab                                                                                                           |
|-------------------|----------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| HTTP/HTTPS Access | `sudo apt install nginx -y`                    | Host a simple web page to test $\text{web-browsing}$ and $\text{ssl}$ $\text{App-IDs}$.                                  |
| Granular App-ID   | `sudo apt install vsftpd -y`                   | Install an $\text{FTP}$ server to test specific application blocking ($\text{ftp}$ $\text{App-ID}$) between zones.       |
| iPerf3 Traffic    | `sudo apt install iperf3 -y and run iperf3 -s` | Generates high-volume, specific traffic to test $\text{iperf}$ $\text{App-ID}$ identification and blocking capabilities. |

I recommend first testing ping connectivity between the $\text{DMZ}$ and the $\text{Trust}$ (`ping 10.1.1.5` or `ping host 10.1.1.5`) and $\text{UnTrust}$ (`8.8.8.8`).

These tests ensure the firewall correctly identifies traffic based on the application itself, regardless of the port number, and enforces policy accordingly.
| Feature Test            | LibreBoard Preparation Command                | Client Action (from Ubuntu-Client)                   | PA-440 Verification & Proof                                                                                                                                                                                  |
|-------------------------|-----------------------------------------------|------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| HTTP Access             | `sudo systemctl start nginx`                    | Browser: Navigate to http://172.16.1.100.            | Success: Verify $\text{web-browsing}$ App-ID is logged ($\text{Trust} \rightarrow \text{DMZ}$).                                                                                                              |
| Granular App-ID Block   | `sudo systemctl start vsftpd`                   | Attempt an $\text{FTP}$ connection: ftp 172.16.1.100 | Deny/Block: Change $\text{Trust} \rightarrow \text{DMZ}$ rule to explicitly Deny the $\text{ftp}$ App-ID. Verify a deny action and Application: ftp in the $\text{Monitor} \rightarrow \text{Traffic}$ logs. |
| Protocol Identification | Run $\text{iperf3}$ in server mode: `iperf3 -s` | Run the client test: iperf3 -c 172.16.1.100          | Identify: Ensure the traffic is logged as Application: iperf. Test blocking the $\text{iperf}$ App-ID to confirm the firewall correctly enforces the denial.                                                 |

## Troubleshooting and Validation
### Netplan Configuration and Activation
If the $\text{La Frite}$ cannot ping its own gateway ($\text{172.16.1.1}$) after running $\text{sudo netplan apply}$:
| Symptom                                           | Cause                                                                                                                                      | Solution                                                                                                                                                                      |
|---------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Error: [Errno 99] Cannot assign requested address | The $\text{YAML}$ file has incorrect indentation (used $\text{Tab}$ instead of $\text{Space}$) or a typo in the IP address/interface name. | Re-run sudo nano /etc/netplan/01-netcfg.yaml. Verify all indentation uses spaces. CRITICAL: Ensure the interface name is correctly typed as $\text{end0}$, not $\text{eth0}$. |
| Old IP Persists                                   | The $\text{NetworkManager}$ process is interfering with $\text{Netplan}$'s static assignment.                                              | Reboot the $\text{La Frite}$. If the problem continues, temporarily stop the manager: sudo systemctl stop NetworkManager.                                                     |
| No Internet Access (Ping Fails to 8.8.8.8)        | The routes section is missing or incorrect.                                                                                                | Ensure the routes section explicitly defines the gateway: via: 172.16.1.1. Check the PA-440 logs for a $\text{DENY}$ action, which indicates the firewall policy is missing.  |

### Physical and PA-440 Connectivity Issues
If the $\text{La Frite}$ is correctly configured but still cannot ping the outside world:
| Symptom                                | Cause                                                                                | Solution                                                                                                                                                                                                                                                         |
|----------------------------------------|--------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| No Link Light                          | Bad cable or the PA-440 port is not active.                                          | Swap the Ethernet cable. On the PA-440 GUI, check $\text{Network} \rightarrow \text{Interfaces} \rightarrow \text{ethernet1/3}$ to ensure the link status is UP/GREEN.                                                                                           |
| Gateway Cannot Be Reached (172.16.1.1) | The subnet mask on the $\text{La Frite}$ is incorrect.                               | On the $\text{La Frite}$, verify the Netplan config uses $\text{/24}$ ($\text{255.255.255.0}$) to match the PA-440.                                                                                                                                              |
| Pings Denied to Trust Zone             | Expected Behavior. The PA-440's implicit security rule blocks traffic between zones. | Verify the PA-440 $\text{Monitor} \rightarrow \text{Traffic}$ log shows a DENY action by the deny-all-interzone rule. This confirms segmentation is WORKING. You must explicitly create a $\text{Trust} \rightarrow \text{DMZ}$ rule to allow $\text{ICMP/SSH}$. |

### User-ID and SSH Access Issues
| Symptom                              | Cause                                                                      | Solution                                                                                                                                                                                                        |
|--------------------------------------|----------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| SSH connection fails from Trust VM   | The $\text{Trust} \rightarrow \text{DMZ}$ policy is blocking $\text{SSH}$. | On the PA-440, ensure an explicit security rule is at the top of the list allowing $\text{Source Zone: Trust}$ to $\text{Destination Zone: DMZ}$ with the $\text{Application: ssh}$ and $\text{Action: Allow}$. |
| SSH access fails (Permission denied) | Local user credentials or service failure.                                 | On the $\text{La Frite}$ console, verify the $\text{ssh}$ service is running (sudo systemctl status ssh) and that you are using the correct user password.                                                 |
