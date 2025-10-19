# Network Segmentation and Zone Configuration

With the system base stable and licenses active, I'm now configuring the physical network segments that define my lab. I'm using dedicated Layer 3 interfaces for each zone, which is critical for making the firewall the central traffic enforcer.
## 1. Configure physical Interfaces

### Physical Interface Overview
I configured $\text{ethernet1/2}$ for the Internet and $\text{ethernet1/1}$ and $\text{ethernet1/3}$ for my internal zones.
| Ethernet Interface | Role/Zone | Interface Type | IP Address  | Virtual Router |
|--------------------|-----------|----------------|-------------|----------------|
| ethernet1/1        | $\text{Trust}$     | Layer3         | 10.1.1.1/24 | default        |
| ethernet1/2        | $\text{UnTrust}$   | Layer3         | DHCP Client | default        |
| ethernet1/3        | $\text{DMZ}$       | Layer3         | 10.1.3.0/24 | default        |

### Step-by-Step Interface Configuration

1. Navigate to Network $\rightarrow$ Interfaces $\rightarrow$ Ethernet.

2. For each interface:

* Click the interface name (e.g., ethernet1/1).
* Set Interface Type to Layer3.
* Set Virtual Router to default.
* L3 Settings (IPv4 Tab):
  * For e1/1 ($\text{Trust}$) and e1/3 ($\text{DMZ}$): Select Static, click Add, and enter the IP address (10.1.1.1/24 and 172.16.1.1/24 respectively).
  * For e1/2 (Untrust): Select DHCP Client to automatically receive an IP.
* Click OK.

## 2. Create Security Zones
Create a Security Zone for each network segment. This is mandatory for enforcing firewall policies between segments.

### Step-by-Step Zone Configuration
1. Navigate to Networks > Zones
2. Click Add and create the following three zones:
   
| Zone Name | Type | Interfaces  | Rationale                                                             |
|-----------|------|-------------|-----------------------------------------------------------------------|
| $\text{Trust}$     | L3   | ethernet1/1 | Enforces policy separation between internal users and other segments. |
| $\text{UnTrust}$   | L3   | ethernet1/2 | Represents the hostile external network.                              |
| $\text{DMZ}$       | L3   | ethernet1/3 | Provides granular access control for perimeter services.              |

3. Ensure the Type is set to L3
4. In the Interfaces box, select and add the corresponding physical interface for each zone.
5. Click OK for each zone.
   
## 3. Configure DHCP Server (Trust Zone)
To make life easy for my client VMs, I set the PA-440 to handle dynamic IP assignment for the $\text{Trust}$ network.

### Step-by-Step DHCP Server Configuration
1. Navigate to Network $\rightarrow$ DHCP $\rightarrow$ DHCP Server.
2. Click Add.
3. General Tab:
   * Interface: Select ethernet1/1.
   * Mode: Select Enabled.
   * Inheritance Source: Select ethernet1/2
   * Inherit Options: Check the boxes for DNS Server, NTP Server, and any other settings you want to pass down from your upstream network.
4. IP Pools Tab:
   * Click Add under IP Pools.
   * Enter the range: 10.1.1.2 - 10.1.1.254.
5. Options Tab (Crucial for Lab Setup):
   * Gateway: Enter 10.1.1.1. (The firewall's own L3 IP).
   * Netmask: Enter 255.255.255.0.
   * Primary DNS: I manually set the primary DNS to 8.8.8.8 and secondary to 8.8.4.4 to ensure my clients can resolve Internet domains immediately.
6. Click Ok.

### Overview
| Interface   | Ip Pools            | Gateway  | Subnet Mask   | Primary DNS | Secondary DNS | 
|-------------|---------------------|----------|---------------|-------------|---------------| 
| ethernet1/1 | 10.1.1.2-10.1.1.254 | 10.1.1.1 | 255.255.255.0 | inherited   | inherited     |

### Static Mappings (Reservations)
Static mappings are required to ensure lab servers maintain consistent addresses, regardless of DHCP. Note that static mappings must still be manually configured to use 10.1.1.4 as their Primary DNS, overriding the inherited option, if you want them to act as internal domain services.
| Address   | Description    |
|-----------|----------------|
| 10.1.1.0  | default        |
| 10.1.1.90 | gui            |
| 10.1.1.5  | ubuntu server  |
| 10.1.1.4  | xubuntu server |

# 4. Configure OSPF Dynamic Routing
This is how I met the L3 routing requirement. I configured OSPF on the default Virtual Router to show that my firewall can dynamically exchange routing information.
## Step-by-Step OSPF General Configuration
1. Navigation: I navigated to Network $\rightarrow$ Virtual Routers and clicked to edit the default Virtual Router.
2. OSPF $\rightarrow$ General Tab
   * I checked Enable OSPF.
   * I set the Router ID to 10.1.1.1 (My Trust interface IP), which is a unique identifier for the firewall in the OSPF domain.
3. OSPF $\rightarrow$ Area Tab:
   * I created Area 0.0.0.0 (the Backbone Area) with the type set to Normal.
4. OSPF $\rightarrow$ Area $\rightarrow$ Interface Tab:
   * I added both my internal Layer 3 interfaces: ethernet1/1 ($\text{Trust}$) and ethernet1/3 ($\text{DMZ}$).
   * I assigned both to Area 0.0.0.0. Rationale: This advertises my internal subnets to any other router (like a simulated core router) that I might add to the lab later.

# 5. Configure NAT Policies
I created a Network Address Translation (NAT) policy to allow my internal hosts to reach the Internet using the firewall's external IP address.
1. Navigate to Policies $\rightarrow$ NAT
2. I created a new policy named `Lab NAT`
   
| Name           | Source Zone | Destination Zone | Source Translation               | Rationale                                                                                                                                                         |
|----------------|-------------|------------------|----------------------------------|-----------------------------------------------------------------------------------------------------|
| Lab NAT        | DMZ, Trust  | untrust          | dynamic-ip-and-port, ethernet1/2 | Allows all internal hosts to reach the Internet by translating their private IPs to the PA-440's public/external IP.                                               |
| Trust-to-Trust | Trust       | Trust            | none                             | Explicitly ensures that traffic staying within the Trust zone is not subject to NAT, which is the default behavior but is documented for clarity/troubleshooting. |

Rationale: This configuration tells the firewall: "Any traffic leaving the $\text{Trust}$ or $\text{DMZ}$ zones and heading for the $\text{Untrust}$ zone should have its source IP address translated to the IP address of the firewall's external interface ($\text{ethernet1/2}$). This is standard Port Address Translation (PAT) for internet access."

# 6. Configure Basic Internet Access Security Policy
Since security rules are processed before NAT, I needed a temporary Security Policy to allow traffic out before I could implement my advanced App-ID policies.
1. Navigate to Policies $\rightarrow$ Security
2. Allow-Outbound-Internet Rule:
   
| Rule Name               | Action | Source Zone | Destination Zone | Application | Service             | Rationale                                                                                            |
|-------------------------|--------|-------------|------------------|-------------|---------------------|-----------------------------------------------------------------------------------|
| Allow-Outbound-Internet | Allow  | Trust, DMZ  | Untrust          | any         | application-default | Permits all internal hosts to access the Internet. (Will be refined with App-ID later).              |
| Allow-Trust-Ping        | Allow  | Trust       | Trust            | ping        | any                 | Explicitly permits ICMP traffic within the Trust network for basic connectivity and troubleshooting. |

Rationale: This rule is deliberately broad (any application/service) to provide initial connectivity. My goal is to refine this later using App-ID and Content-ID profiles to meet the remaining key deliverables.

# 7. Final Commit
If you havent been commiting already, go ahead and do that :)
