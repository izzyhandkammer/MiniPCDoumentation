# Home Lab Deliverables: KSO Project Documentation
This document details the design, configuration, and implementation of a personal home lab built on a Minisforum UM890 mini PC. The objective of this project was to fulfill the KSO Lab Deliverables by establishing a functional and secure network environment that demonstrates key networking and security concepts.

The core of the lab is a virtual Palo Alto Networks firewall (PA-VM), deployed as a central security gateway. This firewall successfully segments a simulated corporate network into three distinct zones: a User Zone for client virtual machines (VMs), a DMZ Zone for a web server VM, and an Untrust Zone representing the internet.

Key deliverables completed as part of this project include:
* The deployment of multiple client and server virtual machines.
* The establishment of L2/L3 connectivity with VLANs and OSPF dynamic routing.
* The configuration of fundamental security policies utilizing Palo Alto Networks' App-ID and Content-ID features.
* The onboarding of the PA-VM to a centralized Panorama management server.
* The implementation of a security policy based on User-ID to demonstrate identity-aware access control.

## Folder Structure
```
  C:\HomeLab\
  ├── VMs\           (Contains all virtual machine files created by VMware)
  ├── ISOs\          (Contains all OS and software installation files)
  └── Docs\          (Contains this documentation and any other project notes)
```
## Hypervisor and VM Deployment
1. **Download OS Images**
   Download [VMWare Workstation Pro](https://access.broadcom.com/default/ui/v1/signin/) and [Ubuntu](https://ubuntu.com/tutorials/install-ubuntu-desktop)
2. **Create Your Virtual Machines**
   * In VMware Workstation, click "Create a New Virtual Machine"
   * Select "I will install the operating system later."
   * For the client VM, choose Linux as the guest OS. For the server, choose Linux.
   * Allocate hardware: 2-4 GB of RAM and 1 CPU for each VM
   * For disk space 20-30 GB (minimum 10 GB) for the Linux server. Ensure to select the option to "Store virtual disk as a single file."
3. **Attach the Installation Media**
   After you create the virtual machine, you must connect the operating system's ```.ISO``` file to the VM's virtual CD/DVD drive. This allows the VM to boot from the installation file and install the operating system
   * With the VM powered off, right-click it in the VMware Workstation library and select "Settings".
   * In the "VM Settings" window, click on the "CD/DVD (SATA)" hardware device.
   * On the right, choose "Use ISO image file:".
   * Click "Browse..." and navigate to your C:\HomeLab\ISOs\ directory to select your Ubuntu ISO file.
   * Make sure the "Connect at power on" checkbox is selected.
   * Click OK to save the settings. The VM will now be ready to boot from the installation media.
