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
