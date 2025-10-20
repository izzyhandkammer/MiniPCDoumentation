# Virtual Machine Deployment and Configuration
This section details how I deployed the virtual machines (VMs) that make up the $\text{Trust}$ and $\text{DMZ}$ zones of my lab on the mini PC running VMware Workstation Pro. This fulfills the "deployment of multiple client and server virtual machines" deliverable.
## Folder Structure
```
  C:\HomeLab\
  ├── VMs\           (Contains all virtual machine files created by VMware)
  ├── ISOs\          (Contains all OS and software installation files)
  └── Docs\          (Contains this documentation and any other project notes)
```
## Hypervisor and VM Deployment
1. **Download OS Images**
   Download [VMWare Workstation Pro](https://access.broadcom.com/default/ui/v1/signin/),  [Ubuntu](https://ubuntu.com/tutorials/install-ubuntu-desktop), and [XUbuntu](https://xubuntu.org/)
2. **Create Your Virtual Machines**
   * In VMware Workstation, click "Create a New Virtual Machine"
   * Select "I will install the operating system later" to allow me to configure the network and hardware before installation.
   * For the client VM, choose Linux (specifically Ubuntu/XUbuntu)
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
  

| VM Name    | Operating System / Role |  vCPUs | vRam | Network Interfaces | IP Address | 
| ---------- | -------                 |   ---- | ---  |                --- |        --- |
| Ubuntu     |   Ubuntu                |   4 GB |    2 |              VMnet4|   10.1.1.5 |
| XUbuntu    |               XUbuntu   |   4 GB |    2 |             VMnet4 |   10.1.1.4 |
| OvaFile    |                         |  32 GB |   12 |             VMnet4 | 10.1.1.20 |

4. **Customizing My VMnets (Crucial for Segmentation)**
   To enforce the separation defined by the PA-440, I had to configure custom virtual switches (VMnets) in VMware Workstation. This is the physical (virtual) foundation of my L3 segmentation.
   1. Open the Virtual Network Editor in VMware (Edit $\rightarrow$ Virtual Network Editor)
   2. I used the following configuration for my custom network:
   
| VMnet Name | Configuration           | PA-440 Interface Connection                | Rationale                                                                              |
|------------|-------------------------|--------------------------------------------|----------------------------------------------------------------------------------------|
| VMnet4     | Host-only (No DHCP/NAT) | $\text{ethernet1/1}$ ($\text{Trust}$ Zone) | Isolates my $\text{Trust}$ traffic; all routing is forced through the $\text{PA-440}$. |

  Note: I ensured the "Connect Host Virtual Adapter to this network" and "Use local DHCP service to distribute IP addresses to VMs" checkboxes were DISABLED for VMnet4. This forces the PA-440 to be the DHCP server.
5. **Configurng the static IP addresses inside the VMs**
Since my PA-440 is acting as the DHCP server for the $\text{Trust}$ network (10.1.1.0/24), the client VMs would normally receive their IPs automatically. However, for a predictable lab environment and fixed server roles, I used static IP assignments inside the OS.
1. Log into the OS
2. Navigate to network config settings (top left wifi symbol $\rightarrow$ netplan-zz-all-en on XUbuntu and via settings in Ubuntu)
3. Configure IP settings for each of the VMs

| VM                | IP address           | Netmask       | Gateway  | DNS     |
|-------------------|----------------------|---------------|----------|---------|
| [Ubuntu, XUbuntu] | [10.1.1.5, 10.1.1.4] | 255.255.255.0 | 10.1.1.1 | 8.8.8.8 |

6. **Testing With Ping**
After configuring the L3 interfaces, OSPF, and the initial security policy, I performed a series of ping tests from my client VMs to verify the logical segmentation and routing were functional.

## Troubleshooting and Challenges Faced
I faced common challenges with VMware Workstation overriding my network settings, which could have disrupted my L3 connectivity deliverable.
* DHCP Interference: VMware's default settings often enable its own DHCP services on Host-only VMnets.
  * Fix: I explicitly checked and disabled the DHCP service for VMnet4 within the Virtual Network Editor.
* IP Address Drift: I had issues where my static IP assignments would occasionally be lost or reset.
  * Fix: I ensured that in the VM's OS, the network connection method was set to Manual or Static, not just a generic "Automatic (DHCP)". I also used the Static Mappings feature on the PA-440 DHCP server to lock the IP addresses, adding redundancy to my static assignments.
  * Firewall Connectivity Issues: When troubleshooting, the first step was always to verify that the VM's network adapter was correctly assigned to VMnet4 (Trust) and that the PA-440 interface (ethernet1/1) was also connected to VMnet4. Mismatched VMnets instantly break the segment.
