# DoSSniffer
DoSSniffer is a software developed as a final course project whose objective is to detect whether the traffic passing through a network interface is benign or corresponds to one of the following DoS attacks:
- UDP flood
- SYN TCP flood
- SNMP amplification attack

Cicflowmeter has been used to obtain the data that passes through the interface and a classification tree model has been previously trained to classify the traffic. Once the data has been processed, it will be sent to InfluxDB, which must be previously configured.

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

The following **Python libraries** will be installed: pandas, watchdog, influxdb-client, libpcap, poetry, and scikit-learn version 1.2.2.

The following **Linux packages** will be installed: build-essential, zlib1g-dev, libncurses5-dev, libgdbm-dev, libnss3-dev, libssl-dev, libreadline-dev, libffi-dev, libpcap-dev, git and wget. 

## Run
    usage: DoSSniffer.py [-h] -i INTERFACE -s SERVER -p PORT
    
    options:
        -h, --help                           show this help message and exit
        -i INTERFACE, --interface INTERFACE  Network interface to monitor
        -s SERVER, --server SERVER           IP address of InfluxDB
        -p PORT, --port PORT                 Port of InfluxDB

**Example:**

    /usr/local/bin/python3.11 DDoSSniffer.py -i enp0s8 -s 192.168.150.10 -p 8086
> **Note:** Make sure to edit the config.json file for a correct connection with InfluxDB. In it, you should define the bucket, token, organization, and measurement (point).
## References
https://www.unb.ca/cic/research/applications.html#CICFlowMeter

https://github.com/hieulw/cicflowmeter/tree/master
