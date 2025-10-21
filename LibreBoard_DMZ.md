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
| HTTP/HTTPS Access | sudo apt install nginx -y                    | Host a simple web page to test $\text{web-browsing}$ and $\text{ssl}$ $\text{App-IDs}$.                                  |
| Granular App-ID   | sudo apt install vsftpd -y                   | Install an $\text{FTP}$ server to test specific application blocking ($\text{ftp}$ $\text{App-ID}$) between zones.       |
| iPerf3 Traffic    | sudo apt install iperf3 -y and run iperf3 -s | Generates high-volume, specific traffic to test $\text{iperf}$ $\text{App-ID}$ identification and blocking capabilities. |
