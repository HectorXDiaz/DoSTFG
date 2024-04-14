import threading
import time
import subprocess
import socket
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import socket
import pickle
import pandas as pd
import influxdb_client
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS
import argparse
import constants
import threading
import psutil
import os


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, event, file_path):
        super().__init__()
        self.event = event
        self.file_path = file_path

    def on_modified(self, event):
        if event.src_path.endswith(self.file_path):
            self.event.set()


class FileWriter(threading.Thread):
    def __init__(self, interface):
        super().__init__()
        self.interface = interface
    def run(self):
        try:
            subprocess.run("sudo poetry run cicflowmeter -i " + self.interface + " -c file.csv", shell=True)
        except OSError as e:
            # Manejar la excepción aquí
            print("Error: La interfaz de red especificada no existe.")

class FileReader(threading.Thread):
    def __init__(self, file_path, event, influxdb_connector):
        super().__init__()
        self.file_path = file_path
        self.event = event
        self.influxdb_connector = influxdb_connector
        self.last_position = 0

    def run(self):
        first_line = True
        while True:
            if not self.event.is_set():
                self.event.wait()

            with open(self.file_path, 'r') as file:
                file.seek(self.last_position)
                # Leer y enviar las líneas del archivo a partir de la segunda línea
                for linea in file:
                    if not first_line:  # Evitar enviar la primera línea
                        procesarmodelo = ProcesadorModelo(self.influxdb_connector, linea)
                        print(linea.strip()) 
                        procesarmodelo.procesar_modelo()  # Llamada al método procesar_modelo
                        time.sleep(1)
                    first_line = False
                self.last_position = file.tell()
                self.event.clear()


class InfluxDBConnector:
    def __init__(self, server, port, bucket):
        self.server = server
        self.port = port
        self.token = os.getenv("INFLUX_TOKEN")
        self.org = os.getenv("INFLUX_ORG")
        self.bucket = bucket

    def connect(self):
        write_client = influxdb_client.InfluxDBClient(url="http://"+self.server+":"+self.port, token=self.token, org=self.org)
        self._test(write_client)
        return write_client.write_api(write_options=SYNCHRONOUS)
    
    def _test(self, client):
        health = client.health()
        if health.status == "pass":
            print("Connection success.")
            return True
        else:
            print(f"Connection failure: {health.message}!")
            return False


class ProcesadorModelo(threading.Thread):
    def __init__(self, influxdb_connector, linea):
        super().__init__()
        self.influxdb_connector = influxdb_connector
        self.linea = linea

    def _procesar_linea(self,):
        fila_primera = "src_ip,dst_ip,src_port,dst_port,protocol,timestamp,flow_duration,flow_byts_s,flow_pkts_s,fwd_pkts_s,bwd_pkts_s,tot_fwd_pkts,tot_bwd_pkts,totlen_fwd_pkts,totlen_bwd_pkts,fwd_pkt_len_max,fwd_pkt_len_min,fwd_pkt_len_mean,fwd_pkt_len_std,bwd_pkt_len_max,bwd_pkt_len_min,bwd_pkt_len_mean,bwd_pkt_len_std,pkt_len_max,pkt_len_min,pkt_len_mean,pkt_len_std,pkt_len_var,fwd_header_len,bwd_header_len,fwd_seg_size_min,fwd_act_data_pkts,flow_iat_mean,flow_iat_max,flow_iat_min,flow_iat_std,fwd_iat_tot,fwd_iat_max,fwd_iat_min,fwd_iat_mean,fwd_iat_std,bwd_iat_tot,bwd_iat_max,bwd_iat_min,bwd_iat_mean,bwd_iat_std,fwd_psh_flags,bwd_psh_flags,fwd_urg_flags,bwd_urg_flags,fin_flag_cnt,syn_flag_cnt,rst_flag_cnt,psh_flag_cnt,ack_flag_cnt,urg_flag_cnt,ece_flag_cnt,down_up_ratio,pkt_size_avg,init_fwd_win_byts,init_bwd_win_byts,active_max,active_min,active_mean,active_std,idle_max,idle_min,idle_mean,idle_std,fwd_byts_b_avg,fwd_pkts_b_avg,bwd_byts_b_avg,bwd_pkts_b_avg,fwd_blk_rate_avg,bwd_blk_rate_avg,fwd_seg_size_avg,bwd_seg_size_avg,cwr_flag_count,subflow_fwd_pkts,subflow_bwd_pkts,subflow_fwd_byts,subflow_bwd_byts"
        dataset = [fila_primera.split(',')]
        dataset.append(self.linea.split(','))
        df = pd.DataFrame(dataset[1:], columns=dataset[0])

        self.src_ip=df['src_ip'].iloc[0]
        self.dst_ip=df['dst_ip'].iloc[0]

        df = df.drop(columns=['src_port', 'dst_port', 'timestamp'])
        df = df.rename(constants.COLUMNAS, axis=1)
        df = df[constants.ORDEN_COLUMNAS]

        return df

    def procesar_modelo(self):
        try:
            df = self._procesar_linea()
            with open('modelo2.pkl', 'rb') as archivo:
                arbol_clasificador = pickle.load(archivo)
            nuevas_predicciones = arbol_clasificador.predict(df)
            print(nuevas_predicciones)

            punto = Point("DDoSnetwork_traffic")
            
            #punto.tag("ip_cliente", psutil.net_if_addrs()["eth1"][0].address)
            punto.tag("nombre_servidor", socket.gethostname())
            punto.tag("ip_origen", self.src_ip)
            punto.tag("ip_destino", self.dst_ip)
       
            
            punto.field("Resultado", int(nuevas_predicciones[0]))
            #punto.field("valor", valor_string)
            
            write_api = self.influxdb_connector.connect()

            write_api.write(bucket=influxdb_connector.bucket, org=influxdb_connector.org, record=punto)
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Procesamiento de datos y escritura en InfluxDB')
    parser.add_argument('-i', '--interface', type=str, help='Interfaz de red a monitorear')
    parser.add_argument('-s', '--server', type=str, help='IP de InfluxDB')
    parser.add_argument('-p', '--port', type=str, help='Puerto de InfluxDB')
    args = parser.parse_args()

    if not all([args.interface, args.server, args.port]):
        parser.error('Se requieren todos los argumentos -i, -s y -p')


    evento_lectura = threading.Event()
    observer = Observer()
    file_change_handler = FileChangeHandler(evento_lectura, 'file.csv')
    observer.schedule(file_change_handler, '.', recursive=False)
    observer.start()

    #url = "http://192.168.100.5:8086"
    #token = "afOLMOf3i9doHYGO-l45bUvrsta4c1PrHdz31PiTmz7WtSRnps0wgIn0tRJcJB-bYGleOjXnmCVtPrC86eKU8Q=="
    #org = "tfg"
    #interface = "eth3"
    
    influxdb_connector = InfluxDBConnector(args.server, args.port, "prueba3")
    
    writer_thread = FileWriter(args.interface,)
    reader_thread = FileReader('file.csv', evento_lectura, influxdb_connector)
    
    writer_thread.start()
    reader_thread.start()

    writer_thread.join()

    observer.stop()
    observer.join()

    print("Programa finalizado.")
