# Centralized Management with Panorama
The next key deliverable is to centralize management of the PA-440 using a Panorama management server. The first step is deploying the Panorama Virtual Machine (VM).

## 1. Deploying the Panorama Virtual Appliance
This process involves downloading the base image from the Palo Alto Networks Customer Support Portal (CSP) and importing it into my hypervisor, VMware Workstation Pro 17.

### 1.1 Download the Panorama OVA File
1. Log into the Palo Alto Networks Customer Support Portal (CSP).
2. Navigate to Updates $\rightarrow$ Software Updates
3. Locate  to "Panorama Base Images"
4. Download `11.2.5-h1 ESX.ova`
   Note: when downloading this in PAB, the file will show itself as locked. You must unlock it in the downloads section before proceeding.

### 1.2 Import the OVA into VMware Workstation
1. Open VMware Workstation Pro 17
2. Open a Virtual Machine
3. Select the downloaded `.ova` file
4. Name the new VM
   need to add about the disc assignment

### 1.3 Initial VM Power-On and CLI Access
1. Once the import was complete, I started the VM
2. After the virtual appliance booted, I accessed the console and logged in using the default credentials `[admin/admin]` (note: it's very common when Panorama boots up for the credentials not to take, just give it ~30 seconds and try again)

### 1.4 Configuring Management Access via CLI
Just like with the PA-440, the first and most critical step is to configure a static IP and change the default password so I can access the Web GUI.
| Action              | Planned Value |
|---------------------|---------------|
| Planned MGT IP      | 10.1.1.19/24 |
| Planned MGT Gateway | 10.1.1.1      |

I used the following structure:
```# Enter configuration mode
configure

# Set the Management Interface to a static IP
Set deviceconfig system ip-address 10.1.1.19
Set deviceconfig system netmask 255.255.255.0
Set deviceconfig system default-gateway 10.1.1.1
Set deviceconfig system dns-setting servers primary 8.8.8.8
Set deviceconfig system ntp-servers primary-ntp-server ntp-server-address north-america.pool.ntp.org

# Commit the configuration
commit

exit
```
### 1.5 Verification
1. After a successful commit, I opened a web browser and navigated to the configured IP address
2. I successfully logged in using my new password, confirming the Panorama VM was up and running.

## 2. Manual Licensing and Activation
After successfully deploying the Panorama VM and setting the management IP, the automatic license retrieval failed. I had to perform a manual activation using the serial number provided by Palo Alto Networks.

### 2.1 Identifying the Device IDs
Although the automated license retrieval process failed, I still needed the unique identifiers (UUID and CPU-ID) for my Panorama VM.
1. Navigate to Device $\rightarrow$ Setup $\rightarrow$ Operations
2. Locate the UUID and CPUID, both unique to your virtual instance

### 2.2 Manually Assigning the Serial Number
1. Navigate to Panorama $\rightarrow$ General Settings
2. In the Serial Number field, I entered the specific serial number provided for my evaluation
3. Click OK
4. I clicked OK. Note: This step took a noticeable amount of time, indicating an auto-commit and registration process was running in the background.
5. After the loading is complete, refresh the page. You will be propted to retrieve licenses (it will fail).
6. Navigate to Licenses, you should see that the license was pulled but the device certificate was missing.

### 2.3 Activating and Uploading the License File
1. Navigate back to Setup and click "Get Certificate".
2. Go to the Customer Support Portal and navigate to Products $\rightarrow$ Device Certificates.
3. Generate an OTP and copy it to the clipboard
4. Paste it into the box and hit Ok.
5. Close the window and track the status on Tasks. Refresh the page after complete and now your Panorama should be officially licensed.

## 3. Onboarding the Firewall to Panorama
Follow [this tutorial](https://www.youtube.com/watch?v=a9W11FptkQQ) and now you've completed the Panorama deliverable!
