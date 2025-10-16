# Network Segmentation and Zone Configuration

This page details the Layer 3 (L3) network segmentation implemented on the Palo Alto Networks PA-VM. Segmentation is achieved by defining different Security Zones and assigning specific VLAN Sub-Interfaces to them. All routing is handled within a single Virtual Router instance.

## Physical Interface Overview
This table defines the function and base configuration of each physical interface.
| Ethernet Interface | Role/Zone | Interface Type | IP Address  | Virtual Router |
|--------------------|-----------|----------------|-------------|----------------|
| ethernet1/1        | Trust     | Layer3         | 10.1.1.0/24 | default        |
| ethernet1/2        | Untrust   | Layer3         | DHCP Client | default        |
| ethernet1/3        | DMZ       | Layer3         |             | default        |

## DHCP Server
The firewall is enabled as a DHCP server on the ethernet1/1 (Trust-Zone) interface to automatically assign IP configurations to clients.
| Interface   | Ip Pools            | Gateway  | Subnet Mask   | Primary DNS | Secondary DNS | 
|-------------|---------------------|----------|---------------|-------------|---------------| 
| ethernet1/1 | 10.1.1.2-10.1.1.254 | 10.1.1.1 | 255.255.255.0 | inherited   | inherited     |

### ethernet1/1 DHCP Server Reserved Ip Addresses
These addresses are reserved from the dynamic pool for specific devices using a static MAC-to-IP binding, ensuring they have consistent addresses.
| Address   | Description    |
|-----------|----------------|
| 10.1.1.0  | default        |
| 10.1.1.90 | gui            |
| 10.1.1.5  | ubuntu server  |
| 10.1.1.4  | xubuntu server |
