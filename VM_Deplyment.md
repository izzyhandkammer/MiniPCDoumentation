
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
  

| VM Name    | Operating System / Role |  vCPUs | vRam | Network Interfaces | IP Address | 
| ---------- | -------                 |   ---- | ---  |                --- |        --- |
| Ubuntu     |   Ubuntu                |   4 GB |    2 |              VMnet4|   10.1.1.5 |
| XUbuntu    |               XUbuntu   |   4 GB |    2 |             VMnet4 |   10.1.1.4 |
| OvaFile    |                         |  32 GB |   12 |             VMnet4 | 10.1.1.20 |

