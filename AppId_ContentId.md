# Configuration of App-ID and Content-ID Security Policies
The goal of this deliverable is to transition my firewall from simple port-based access to a true Next-Generation Firewall (NGFW) by enforcing policy based on App-ID (what the traffic is) and Content-ID (what threats the traffic contains).

## Policy Refinement using App-ID
I replaced the temporary, broad "Allow-Outbound-Internet" rule with a refined policy that explicitly allows only necessary applications (like $\text{web-browsing}$ and $\text{ssl}$) and uses App-ID instead of port numbers. This immediately blocks unauthorized applications without blocking the ports they use.

### Step-by-Step Security Rule Configuration
1. Navigate to Policies $\rightarrow$ Security and located the initial permissive rule
2. Rename the temporary rule to Outbound-Basic-Access
3. Application Tab: Change the application list from any to the following specific App-IDs:
   * $\text{web-browsing}$ (Standard HTTP traffic)
   * $\text{ssl}$ (Standard HTTPS traffic)
   * $\text{dns}$ (Domain Name System resolution)
   * $\text{ntp}$ (Network Time Protocol synchronization)
4. Service Tab: ensure the Service remains set to application-default. This forces the firewall to identify the application first, then check if the traffic is using its standard port (e.g., $\text{web-browsing}$ on port 80)
5. New DMZ Access Rule: I created a second rule, DMZ-Web-Access, to allow external users to reach my web server:
   * Destination Zone: $\text{DMZ}$
   * Destination Address: Set to the Address Object for my web server's IP (e.g., 10.1.3.10)
   * Application: Limited to $\text{web-browsing}$ and $\text{ssl}$

## Threat Prevention with Content-ID
Content-ID is implemented by creating and applying Security Profiles to the policy rules. This enables the firewall to inspect the packet payload for malware, vulnerabilities, and risky web categories.

### Step 1: Creating the Security Profile Group
1. Navigate to Objects $\rightarrow$ Security Profile Groups
2. Create a new group named KSO-Default-Profiles
3. Attatch the following default profiles to this group:

| Security Profile Type    | Profile Used     | Content-ID Function                                                          |
|--------------------------|------------------|------------------------------------------------------------------------------|
| Antivirus                | $\text{default}$ | Scans files for known malware signatures.                                    |
| Vulnerability Protection | $\text{default}$ | Blocks attempts to exploit known software vulnerabilities.                   |
| Spyware                  | $\text{default}$ | Blocks communication with known Command-and-Control (C2) servers.            |
| URL Filtering            | $\text{default}$ | Prevents access to websites categorized as malicious, illegal, or high-risk. |

### Step 2: Applying Profiles to Policy
1. Return to Policies $\rightarrow$ Security
2. Edit the `Outbound-Basic-Access` rule
3. Action Tab $\rightarrow$ Profile Settings: select the `KSO-Default-Profiles` group from the Profile Type drop-down menu
4. I repeated this step for the `DMZ-Web-Access` rule.
   
By applying these profiles, the firewall now actively subjects all allowed outbound traffic to threat inspection, successfully completing the Content-ID deliverable.

### Step 3: Commit!
