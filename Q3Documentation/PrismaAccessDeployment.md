# Deploying Prisma Access Infrastructure and configuring Mobile Users
## 1. Initial Infrastructure Configuration
1. Navigate to SCM > Configuration > NGFW and Prisma Access
2. Set the Configuration Scope to Prisma Access
3. Enable GlobalProtect
4. Once the GlobalProtect activation is processed, select it from the Overview section to begin detailed configuration

## 2. Infrastructure & Location Settings
* Infrastructure Tab:
   Portal Hostname: `izzy.lab.gpcloudservice.com` and all other infrastructure settings remain at their default
* Prisma Access Locations: Select `US West` `US South` `US Northeast`

## 3. GlobalProtect App Config
* Select the GlobalProtect App tab
* Under App Settings, select `Default`
* In the App Configuration box, click Show Advanced Options > User Behavior
* Configure DEM for Prisma Access: select `User cannot Enable or Disable DEM`
* Click Save

## 4. Identity Services
Before the configuration is pushed, a local user must be created to test the initial connection
* On the top navigation bar, select Identity Services > Local Users & Groups
* Select Add Local User and create credentials
* Save
* Push Config at Prisma Access scope (Note: Expect 1–2 hours for the infrastructure to fully provision. Don't freak out if SCM seems broken.)

## 5. Client Deployment & Verification
Once the cloud status is green, deploy the agent to the test endpoint
* In browser, navigate to the portal hostname
* Login with the credentials you provided
* Download and run the app
* Use the hostname as the portal, and log in to the agent

Verification Success: The GlobalProtect icon in the system tray should show a "Connected" status with a shield icon

# ADEM for MU
## 1. Defining the Application Suite
* Navigate to SCM > Insights > Application Experience
* Click the configuration icon in the top right corner
* On the Application Suites tab, select Create Application Suite
* Configure the suite: Name: `youtube` Add Domain: `www.youtube.com`
* Save

## 2. Creating Application Tests
* Switch to the Application Tests tab
* Select Create Application Test
* Configure the test: Name: `youtube` Add Domain URL: `www.youtube.com`
* Save

## 3. Verification & Insights
* On the test machine connected via GlobalProtect, browse to YouTube and run video content for 10–20 minutes
* Return to the SCM > Insights > Application Experience dashboard
* Review the Application tab to see metrics

# Configure Service Connection
Note: The single most important thing with the service connection is consistency accross the firewall and SCM
## 1. SCM Configuration
1. Navigate to Configuration > NGFW and Prisma Access > Service Connections.
2. Add a service connection with Prisma Access Location: `US South PA-G`
3. Under Primary Tunnel, select Setup
   * Name the tunnel
   * Branch Device Type: `Other Devices`
   * Branch Device IP Address: `Dynamic`
   * Create your pre-shared key
  
Tip: Commit your changes in SCM now. This generates the necessary FQDNs and infrastructure on the backend which you will need for the local firewall configuration

4. Identification Settings
   * IKE Local Identification: `FQDN(hostname)` `<your FQDN>`
   * IKE Peer Identification: `User FQDN(email address)` `<your email>`
5. Advanced Options
   * Enable IKE Passive Mode
   * IKE Protocol Version: `IKEv2 only mode`
6. IKEv2 Crypto Profile (create new)
   * Encryption: `aes-256-cbc`
   * Authentication: `sha256`
   * DH Group: `group20`
   * Lifetime: `8 hours`
   * Disable AKE

## 2. Local Firewall Configuration
Now, configure the local side of the tunnel to match the cloud parameters
1. Crypto Profiles
   * IKE Crypto (Network > IKE Crypto):
   * Use the same name
   * Settings: DH Group 20, SHA256, AES-256-CBC, 8hr Lifetime
2. IPSec Crypto (Network > IPSec Crypto):
   * Use the same name
   * Settings: ESP, AES-256-CBC, SHA256, DH Group 20, 8hr Lifetime
3. IKE Gateway (Network > IKE Gateways):
   * Interface: `<your untrust>`
   * Peer Address `<your peer address>`
   * Authentication: `<your PSK>`
   * Local ID: `User FQDN`
   * Peer ID: `FQDN`
     (make sure these are mirrored from the cloud config)
   * Advanced: Enable NAT Traversal; Select your created IKE Crypto Profile
4. Tunnel Interface (Network > Interfaces > Tunnel):
   * Name: `tunnel.2`
   * Virtual Router: `default`
   * Security Zone: `s2s` (New zone required)
5. Navigate to Network > IPSec Tunnels > Add:
   * Name: `sc-lab`
   * Tunnel Interface: `tunnel.2`
   * IKE Gateway
   * IPSec Crypto Profile

## 3. Tunnel Verification
Unlike traditional tunnels, we will manually trigger the negotiation from the local CLI
1. Log onto the 440 cli
2. `test vpn ipsec-sa tunnel sc-lab`
3. Be patient. If the tunnel doesn't come up immediately, verify your Peer IDs and ensure the config push in SCM completed successfully.
