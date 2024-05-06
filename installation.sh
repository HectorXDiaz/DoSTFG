#!/bin/bash
mkdir temporal

# Actualizar e instalar actualizaciones
sudo apt-get update
sudo apt-get upgrade

# Instalación de Python
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget
wget -P temporal https://www.python.org/ftp/python/3.11.3/Python-3.11.3.tgz
tar -xvf temporal/Python-3.11.3.tgz -C temporal/
cd temporal
sudo ./Python-3.11.3/configure --enable-optimizations
sudo make -j $(nproc)
sudo make altinstall 
cd ..

# Instalación de dependencias Python
sudo pip3.11 install pandas watchdog influxdb-client libpcap poetry
sudo pip3.11 install scikit-learn==1.2.2
#sudo pip3.11 install poetry

# Instalación de dependencias del sistema
sudo apt-get install -y libpcap-dev
sudo apt install -y git

#Descarga de repositorios cicflowmeter
sudo git clone https://github.com/hieulw/cicflowmeter temporal/cicflowmeter
sudo mv temporal/cicflowmeter/* .
#sudo mv DDoSSniffer/temporal/DDoSTFG/* DDoSSniffer

#Instalación cicflowmeter
#cd DDoSSniffer
sudo poetry install
#cd ..

#Limpieza ficheros
sudo rm -drf temporal
