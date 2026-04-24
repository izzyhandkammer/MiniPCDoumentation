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
