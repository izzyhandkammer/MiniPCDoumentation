# Network Segmentation and Zone Configuration

This page details the Layer 3 (L3) network segmentation implemented on the Palo Alto Networks PA-VM. Segmentation is achieved by defining different Security Zones and assigning specific VLAN Sub-Interfaces to them. All routing is handled within a single Virtual Router instance.

| Ethernet Interface | Role/Zone | Interface Type | IP Address  | Virtual Router |
|--------------------|-----------|----------------|-------------|----------------|
| ethernet1/1        | Trust     | Layer3         | 10.1.1.0/24 | default        |
| ethernet1/2        | Untrust   | Layer3         | DHCP Client | default        |
| ethernet1/3        | DMZ       | Layer3         |             | default        |
