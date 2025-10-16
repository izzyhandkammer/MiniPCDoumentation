# Network Segmentation and Zone Configuration

This page details the Layer 3 (L3) network segmentation implemented on the Palo Alto Networks PA-VM. Segmentation is achieved by defining different Security Zones and assigning specific VLAN Sub-Interfaces to them. All routing is handled within a single Virtual Router instance.
## 1. Configure physical Interfaces

### Physical Interface Overview
This table defines the function and base configuration of each physical interface.
| Ethernet Interface | Role/Zone | Interface Type | IP Address  | Virtual Router |
|--------------------|-----------|----------------|-------------|----------------|
| ethernet1/1        | Trust     | Layer3         | 10.1.1.0/24 | default        |
| ethernet1/2        | Untrust   | Layer3         | DHCP Client | default        |
| ethernet1/3        | DMZ       | Layer3         |             | default        |

### Step-by-Step Interface Configuration

1. Navigate to Network > Interfaces > Ethernet.

2. For each interface:

* Click the interface name (e.g., ethernet1/1).
* Set Interface Type to Layer3.
* Set Virtual Router to default.
* L3 Settings (IPv4 Tab):
  * For e1/1 (Trust) and e1/3 (DMZ): Select Static, click Add, and enter the IP address (10.1.1.1/24 and 172.16.1.1/24 respectively).
  * For e1/2 (Untrust): Select DHCP Client to automatically receive an IP.
* Click OK.

## 2. Create Security Zones
Create a Security Zone for each network segment. This is mandatory for enforcing firewall policies between segments.

### Step-by-Step Zone Configuration
1. Navigate to Networks > Zones
2. Click Add and create the following three zones:
   
| Zone Name | Type | Interfaces  | Rationale                                                             |
|-----------|------|-------------|-----------------------------------------------------------------------|
| Trust     | L3   | ethernet1/1 | Enforces policy separation between internal users and other segments. |
| Untrust   | L3   | ethernet1/2 | Represents the hostile external network.                              |
| DMZ       | L3   | ethernet1/3 | Provides granular access control for perimeter services.              |

3. Ensure the Type is set to L3
4. In the Interfaces box, select and add the corresponding physical interface for each zone.
5. Click OK for each zone.
   
## 3. Configure DHCP Server (Trust Zone)
The PA-VM will handle dynamic IP assignment for the Trust network, pushing the necessary network and DNS settings to clients.

### Step-by-Step DHCP Server Configuration
1. Navigate to Network > DHCP > DHCP Server.
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
   * Primary DNS: Set this field to Inherited (or leave it blank if the inheritance box is checked)
       * Rationale (Inherited): This passes the DNS server IP (e.g., your ISP's DNS or 8.8.8.8 if your upstream router uses it) received by ethernet1/2 to your Trust clients.
   * Secondary DNS: Set this field to Inherited (if applicable) or leave it blank.
6. Click Ok.

### Overview
| Interface   | Ip Pools            | Gateway  | Subnet Mask   | Primary DNS | Secondary DNS | 
|-------------|---------------------|----------|---------------|-------------|---------------| 
| ethernet1/1 | 10.1.1.2-10.1.1.254 | 10.1.1.1 | 255.255.255.0 | inherited   | inherited     |

### Static Mappings (Reservations)
Static mappings are required to ensure lab servers maintain consistent addresses, regardless of DHCP. Note that static mappings must still be manually configured to use 10.1.1.4 as their Primary DNS, overriding the inherited option, if you want them to act as internal domain services.| Address   | Description    |
|-----------|----------------|
| 10.1.1.0  | default        |
| 10.1.1.90 | gui            |
| 10.1.1.5  | ubuntu server  |
| 10.1.1.4  | xubuntu server |

# 4. Configure OSPF Dynamic Routing
You need to configure the Open Shortest Path First (OSPF) protocol on the PA-VM's Virtual Router to dynamically share routing information with any simulated core router in your lab (or to simply advertise your connected networks).

## Step-by-Step OSPF General Configuration
i need to do this and understand whats up

# 5. Configure NAT Policies
Navigate to Policies > NAT
## Overview
| Name           | Source Zone | Destination Zone | Source Translation               | Rationale                                                                                                                                                         |
|----------------|-------------|------------------|----------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Lab NAT        | DMZ, Trust  | untrust          | dynamic-ip-and-port, ethernet1/2 | Allows all internal hosts to reach the Internet by translating their private IPs to the PA-VM's public/external IP.                                               |
| Trust-to-Trust | Trust       | Trust            | none                             | Explicitly ensures that traffic staying within the Trust zone is not subject to NAT, which is the default behavior but is documented for clarity/troubleshooting. |

# 6. Configure Basic Internet Access Security Policy
While a full security policy is a later step, you need a basic rule to allow internal traffic to exit the firewall and reach the Internet.

| Rule Name               | Action | Source Zone | Destination Zone | Application | Service             | Rationale                                                                                            |
|-------------------------|--------|-------------|------------------|-------------|---------------------|------------------------------------------------------------------------------------------------------|
| Allow-Outbound-Internet | Allow  | Trust, DMZ  | Untrust          | any         | application-default | Permits all internal hosts to access the Internet. (Will be refined with App-ID later).              |
| Allow-Trust-Ping        | Allow  | Trust       | Trust            | ping        | any                 | Explicitly permits ICMP traffic within the Trust network for basic connectivity and troubleshooting. |

# 7. Final Commit
If you havent been commiting already, go ahead and do that :)
