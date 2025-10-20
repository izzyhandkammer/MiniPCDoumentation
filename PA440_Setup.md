# Palo Alto Networks PA-440 Deployment

## 1. Prerequisites and Planning
This initial phase outlines the groundwork and necessary information gathered before touching the physical firewall. I highly recommend completing this section before unboxing the PA-440.
### 1.1 Network Topology and Role
* My PA-440 is the heart of my KSO homelab, acting as the security enforcement point for all traffic.
* I decided to deploy this homelab at my office location rather than my home. This meant I needed to acquire and configure my own dedicated T-Mobile Router to act as the gateway/modem, providing the internet connection for my firewall.
* I used a lucid chart diagram to visualize all my physical and logical connections. Unlike a trunked VLAN setup, I've used dedicated Layer 3 interfaces on the PA-440 for each zone ($\text{ethernet1/1}$, $\text{ethernet1/2}$, and $\text{ethernet1/3}$).
### 1.2 Administrative Preparation
I made sure all my licensing and access information was ready to go so the setup process would be smooth. 
* Palo Alto Support Portal Check:
  * I confirmed that I had an active Palo Alto Networks Support Portal account.
  * I used the serial number from the device [PA-440-S/N I used] to register the physical appliance as an asset under my account.
  * CRITICAL STEP (Licensing): I ensured the necessary evaluation licenses for the PA-440 (e.g., Threat Prevention, URL Filtering) were approved and tied to my device's serial number in the portal. This step can take a few days.
* Initial Access Plan (First Boot):
  * I chose to use my Console Cable and CLI for the absolute first boot. This prevents any networking issues from locking me out before the Web GUI is accessible.
* Management Configuration Plan
  * I planned a dedicated management IP that sits within my T-Mobile router's subnet for initial access.

## 2. Initial Device Configuration (CLI)
This stage covers powering on the device, establishing console access, securing the firewall, and setting up the basic management network.
### 2.1 Physical Connection and Console Access
1. Power On: I connected the PA-440 to power and waited for the Power LED (PWR) to turn solid green and the device to finish booting (the process takes several minutes).
2. Console Connection: I connected my laptop to the Console port on the PA-440 using the console cable (USB to RJ-45).
3. Terminal Session: I opened my terminal emulator ([e.g., PuTTY]) and configured the settings: $\text{9600 baud, 8 data bits, no parity, 1 stop bit, no flow control}$.
4. Login: Once the prompt appeared, I logged in with the default credentials: admin/admin.

### 2.2. Securing the Firewall (Mandatory Step)
The absolute first task was to change the default password.
1. Enter Configuration Mode
   `configure`
   Changes prompt from `>` to `#`
2. Set New Password
   `set mgt-config users admin password`
   Should prompt to enter and confirm strong admin password
3. Commit Changes
   `commit`
   Wait for the "Configuration committed successfully" message"
   
### 2.3 Configuring Management Access
I configured the dedicated MGT interface with the planned static IP address so I could reach the Web GUI without having the firewall on the production network yet. I highly recommend this approach as I don't know of a single person who had an easy time with the GUI approach.
1. Set MGT Interface Type
   `set deviceconfig system type static`
   This ensures the MGT interface uses my static IP, not DHCP
2. Set MGT IP Address and Netmask
   `set deviceconfig system ip-address 10.1.1.90 netmask 255.255.255.0`
3. Set Default Gateway
   `set deviceconfig system default-gateway 10.1.1.1`
   This is the IP of my T-Mobile Router for management access.
4. Set Hostname
   `set deviceconfig system hostname Izzys-PA-440`
5. Commit changes
   `commit`

### 2.4 Initial Web GUI Access
After the commit, I disconnected the console cable and moved to the Web GUI:
1. Physical Connection: I connected my laptop to the MGT port on the PA-440
2. Browser: I opened my browser and navigated to https://10.1.1.90
3. Login: I logged in using the username admin and my newly set password
4. Verification: I checked the Dashboard to confirm the hostname was correctly set

## 3. Base System Configuration
I performed these configurations via the Web GUI to establish a stable and functional base environment.
### 3.1 General System and Time Settings
Accurate time is essential for logging, certificate validation, and general security operations.
1. Navigation: navigate to Device $\rightarrow$ Setup $\rightarrow$ Management
2. Confirm your set Hostname
3. Time Settings (NTP): Under the NTP tab, add the Primary Server as `north-america.pool.ntp.org`
4. DNS Settings: Under the Services tab, Set the primary DNS server to 8.8.8.8 and the secondary DNS server to 8.8.4.4
### Licensing and Content Updates (Crucial Step)
This step activates the security features required for my key deliverables (App-ID and Content-ID)
1. Navigation: Navigate to Device $\rightarrow$ Licenses
2. Activation:
   * I clicked Retrieve licenses from license server to pull the evaluation licenses tied to my serial number.
   * I verified that all essential licenses (e.g., Threat Prevention, WildFire, URL Filtering) showed an Active status.
3. Dynamic Updates:
   * I navigated to Device $\rightarrow$ Dynamic Updates.
   * I manually downloaded and installed the latest versions of:
     *  Applications and Threats (for App-ID functionality).
     *  Antivirus (for Content-ID functionality).
### 3.3 Final Commit
Go ahead and commit it! Now you're ready to move into interface configuration and zoning.
