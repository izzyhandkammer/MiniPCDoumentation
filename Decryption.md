# SSL Decryption and Advanced Traffic Control

## 1. Preparation and CA Setup
To enable decryption, the firewall must create its own trust chain to sign certificates presented by external websites. This requires a Root Certificate Authority (CA).

### 1.1 Create the Self-Signed Root CA
* Log into the PA-440 GUI and navigate to Device $\rightarrow$ Certificate Management $\rightarrow$ Certificates.
* Click Generate to create the new Root CA
* Details:
  * Name: `Corp-Root-CA`
  * Common Name: `izzy home lab`
  * Signed By: Self-Signed
  * Certificate Authority: Checked
    
### 1.2 Generate Decryption Certificates
Generate two specialized certificates used for the decryption process:
* Forward Trust Certificate:
  * Purpose: This certificate is used to re-sign certificates from sites the PA-440 trusts. This certificate is signed by the `Corp-Root-CA`.
  * Generate Details: Signed By $\rightarrow$ Selected `Corp-Root-CA`.
* Forward Untrust Certificate:
  * Purpose: This certificate is used to break the connection to sites the PA-440 considers untrustworthy (e.g., sites with expired certificates).
  * This certificate is Self-Signed.

### 1.3 Identify Target VM
I am only decrypting traffic from one VM [xUbuntu, 10.1.1.4]

## 2. Creating the Decryption Policy
I created a specific policy to tell the firewall what traffic to decrypt.
1. Navigate to Policies $\rightarrow$ Decryption
2. Create a new rule named Decrypt-Trust-Vms

| Source Zone | Source Address | Destination | Service/URL Category | Options                                                             |
|-------------|----------------|-------------|----------------------|---------------------------------------------------------------------|
| Trust       | 10.1.1.4       | Any         | Any                  | [Action: Decrypt], [Type: SSl Forward Proxy], [Decryption Profile: Default |

## 3. Client-Side Certificate Installation
For decryption to work without browser warnings, the client VM must trust the PA-440's new Root CA.
1. Export Root CA: On the PA-440, I exported the `Corp-Root-CA` certificate as a $\text{.cer}$ file.
2. Transfer to Client: I uploaded the certificate file to Google Drive and downloaded it onto the client VM.
3. Terminal Installation (xUbuntu): I installed the certificate into the operating system's trust store:
* `cd` into the downloads folder
* Run `sudo cp cert_Corp-Root-CA.cert /usr/local/share/ca-certificates/`.
* Run `sudo update-ca-certificates`.
4. Firefox Installation: Manually import the certificate into Firefox's certificate store via the Settings $\rightarrow$ Privacy & Security $\rightarrow$ View Certificates menu, selecting the option to trust the CA for websites

## 4. Verification and QUIC Traffic Control
After committing the Decryption Policy, I verified it was working and used the new visibility to block the QUIC protocol.

### 1. Decryption Verification
1. Commit on the PA-440 to apply the Decryption Policy.
2. Test: From the client VM, go to any site.
3. Verification: Inspect the site's certificate in the browser. The connection was verified by the PA-440's Forward Trust Certificate (signed by Corp-Root-CA), proving decryption was successful.
4. Navigating to Monitor $\rightarrow$ Logs on the firewall shows the decrypted traffic flows and enhanced visibility.

### 2. Blocking QUIC Traffic
QUIC is an encrypted Google-developed protocol ($\text{UDP}$ port 443) that bypasses traditional $\text{HTTPS}$ inspection, even with decryption enabled. Blocking it forces browsers to use standard $\text{HTTPS}$, ensuring full security visibility.

1. QUIC Denial Policy: I created a new Security Policy named Deny-QUIC-Traffic

| Source Zone | Destination | Application | Action |
|-------------|-------------|-------------|--------|
| Trust       | UnTrust     | quic        | Deny   |

2. Policy Order: I moved the Deny-QUIC-Traffic policy to the top of the policy list (above my Outbound-Basic-Access rule) to ensure it is processed first.
3. Final Commit: I committed the new QUIC denial policy.
4. Verification: I browsed to Google Drive or a Google search page. I observed the firewall's $\text{Monitor}$ tab actively blocking the $\text{quic}$ $\text{App-ID}$ traffic, confirming the policy forced the traffic to fall back to the fully inspected $\text{ssl}$ protocol.
