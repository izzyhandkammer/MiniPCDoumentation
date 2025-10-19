# Home Lab Deliverables: KSO Project Documentation
This document details the design, configuration, and implementation of a personal home lab built on a Minisforum UM890 mini PC. The objective of this project was to fulfill the KSO Lab Deliverables by establishing a functional and secure network environment that demonstrates key networking and security concepts.

The core of the lab is a virtual Palo Alto Networks firewall (PA-VM), deployed as a central security gateway. This firewall successfully segments a simulated corporate network into three distinct zones: a User Zone for client virtual machines (VMs), a DMZ Zone for a web server VM, and an Untrust Zone representing the internet.

## Key Deliverables:
* The deployment of multiple client and server virtual machines.
* The establishment of L2/L3 connectivity with VLANs and OSPF dynamic routing.
* The configuration of fundamental security policies utilizing Palo Alto Networks' App-ID and Content-ID features.
* The onboarding of the PA-VM to a centralized Panorama management server.
* The implementation of a security policy based on User-ID to demonstrate identity-aware access control.

# Table of Contents
1. [VM Deployment](VM_Deplyment.md)
2. [Network Segmentation and Zone Deployment](Segmentation_Zones.md)

# To Do:
* verify the IP address of my management interface and change it within my setup documentation.
* update table of contents and order
* add visual intrigue to my 440 setup page
* cross check my osfp info in routing
* update panorama onboarding section with relavent ip address, disc allocation (only need 4 cores), and steps beyond my problem
