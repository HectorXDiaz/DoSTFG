#!/bin/bash
mkdir DDoSSniffer
mkdir DDoSSniffer/temporal

# Actualizar e instalar actualizaciones
sudo apt-get update
sudo apt-get upgrade

# Instalación de Python
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget
wget -P DDoSSniffer/temporal https://www.python.org/ftp/python/3.11.3/Python-3.11.3.tgz
tar -xvf DDoSSniffer/temporal/Python-3.11.3.tgz -C DDoSSniffer/temporal/
cd DDoSSniffer/temporal
sudo ./Python-3.11.3/configure --enable-optimizations
sudo make -j $(nproc)
sudo make altinstall 
cd ../..

# Instalación de dependencias Python
sudo pip3.11 install pandas watchdog influxdb-client libpcap poetry
sudo pip3.11 install scikit-learn==1.2.2
#sudo pip3.11 install poetry

# Instalación de dependencias del sistema
sudo apt-get install -y libpcap-dev
sudo apt install -y git

#Descarga de repositorios cicflowmeter
sudo git clone https://github.com/hieulw/cicflowmeter DDoSSniffer/temporal/cicflowmeter
sudo mv DDoSSniffer/temporal/cicflowmeter/* DDoSSniffer
sudo git clone https://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@github.com/HectorXDiaz/DDoSTFG DDoSSniffer/temporal/DDoSTFG
sudo mv DDoSSniffer/temporal/DDoSTFG/* DDoSSniffer

#Instalación cicflowmeter
cd DDoSSniffer
sudo poetry install
cd ..

#Limpieza ficheros
sudo rm -drf DDoSSniffer/temporal

# Verifica si la variable de entorno existe
check_env_variable() {
    if [ -z "${!1}" ]; then
        return 1  # La variable de entorno no existe
    else
        return 0  # La variable de entorno existe
    fi
}

# Pide al usuario que ingrese el valor de la variable de entorno
prompt_env_variable() {
    read -p "Por favor, ingrese el valor de $1: " value
    export $1="$value"
}

# Comprueba si la variable de entorno existe y la solicita al usuario si no existe
check_and_prompt() {
    if ! check_env_variable "$1"; then
        prompt_env_variable "$1"
    fi
}

# Lista de variables de entorno que deseas verificar
variables=("INFLUX_TOKEN" "INFLUX_ORG")

# Comprueba cada variable de entorno y solicita al usuario si no existe
for var in "${variables[@]}"; do
    check_and_prompt "$var"
done

# Agrega las variables de entorno al archivo /etc/environment
for var in "${variables[@]}"; do
    echo "$var=\"${!var}\"" | sudo tee -a /etc/environment >/dev/null
done

echo "Variables de entorno configuradas correctamente en /etc/environment."
