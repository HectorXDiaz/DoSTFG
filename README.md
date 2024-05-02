# DoSSniffer
Introduction
## Requirements
Linux and Python modules requirements
## Installation
The installation file requires **execute permissions** and must be run with **sudo**.

    git clone https://github.com/HectorXDiaz/DoSTFG
    chmod +x DosTFG/installation.sh
    cd DosTFG
    sudo ./installation.sh
    
## Run
    /usr/local/bin/python3.11 DDoSSniffer.py -i enp0s8 -s 192.168.150.10 -p 8086
Configure config.json file
Make sure it is possible access to InfluxDB and port is opened
