# Prerecs
1. need a device that stays on most of the time. i chose a raspberry pi zero W with Linux installed on the boot media
2. use the raspberry pi imager to follow the instructions for [headless setup](https://www.raspberrypi.com/documentation/computers/getting-started.html#headless-setup)
	1. install python and all dependencies
		1.  `sudo apt update && sudo apt upgrade -y`
		2. `sudo apt install python3-pip python3-venv -y`
		3. `sudo apt install git`
		4. `mkdir scan`
		5. `cd scan`
	2. sudo apt update && sudo apt install python3 python3-pip -y
	3. pip3 install requests

# Steps
1. Create a new role for the device to write alerts and use the info to fill out an env file with 
2. generate an API key through XDR Settings → configurations → new key

need to pull in python to pi
need to create baseline list of devices currently on the network