# DoSSniffer
A system developed as a final course project whose objective is to detect whether the traffic passing through a network interface is benign or corresponds to one of the following DoS attacks:
- UDP flood
- SYN TCP flood
- SNMP amplification attack

Cicflowmeter has been used to obtain the data that passes through the interface and a classification tree model has been previously trained to classify the traffic.

## Requirements

- Linux system
> **Note:** The system has been tested exclusively on Debian 11; therefore, it cannot be guaranteed to work on another Linux distribution.
- Python 3.11
- InfluxDB

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
