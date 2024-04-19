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
import json

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
            print("Error: The specified network interface does not exist.")

class FileReader(threading.Thread):
    def __init__(self, file_path, event, influxdb_connector):
        super().__init__()
        self.file_path = file_path
        self.event = event
        self.influxdb_connector = influxdb_connector

    def run(self):
        last_position = 0
        first_line = True
        while True:
            if not self.event.is_set():
                self.event.wait()
            with open(self.file_path, 'r') as file:
                file.seek(last_position)
                for linea in file:
                    if not first_line:  
                        process = ModelProcessor(self.influxdb_connector, linea)
                        print(linea.strip()) 
                        process.process_model()
                        time.sleep(1)
                    first_line = False
                last_position = file.tell()
                self.event.clear()

class InfluxDBConnector:
    def __init__(self, server, port, bucket, token, org, pointName):
        self.server = server
        self.port = port
        self.bucket = bucket
        self.token = token
        self.org = org
        self.pointName = pointName

    def connect(self):
        write_client = influxdb_client.InfluxDBClient(url="http://"+self.server+":"+self.port, token=self.token, org=self.org)
        self._test(write_client)
        return write_client.write_api(write_options=SYNCHRONOUS)
    
    def write(self, point):
        write_api = self.connect()
        write_api.write(bucket=self.bucket, org=self.org, record=point)
    
    def point(self, prediction, src_ip, dst_ip):
        point = Point(self.pointName)
        point.tag("nombre_servidor", socket.gethostname())
        point.tag("ip_origen", src_ip)
        point.tag("ip_destino", dst_ip)    
        point.field("Resultado", int(prediction))

        return point
    
    def _test(self, client):
        health = client.health()
        if health.status == "pass":
            print("Connection success.")
            return True
        else:
            print(f"Connection failure: {health.message}!")
            return False
        
class JsonConfig:
    def __init__(self, file_path):
        self.file_path = file_path
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.file_path, 'r') as f:
                config = json.load(f)
            return config
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error: The file {self.file_path} was not found.") from e
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Error: The file {self.file_path} has an incorrect JSON format.") from e

    def field(self, value):
        if value not in self.config:
            raise KeyError(f"Error: The field '{value}' is not present in the configuration.")
        return self.config[value]

class ModelProcessor:
    def __init__(self, influxdb_connector, linea):
        self.influxdb_connector = influxdb_connector
        self.linea = linea

    def _process_line(self,):
        dataset = [constants.FIRST_ROW.split(',')]
        dataset.append(self.linea.split(','))
        df = pd.DataFrame(dataset[1:], columns=dataset[0])

        self.src_ip=df['src_ip'].iloc[0]
        self.dst_ip=df['dst_ip'].iloc[0]

        df = df.drop(columns=['src_port', 'dst_port', 'timestamp'])
        df = df.rename(constants.COLUMNAS, axis=1)
        df = df[constants.ORDEN_COLUMNAS]

        return df

    def process_model(self):
 
        df = self._process_line()
        with open('modelo.pkl', 'rb') as archivo:
            classifier_tree = pickle.load(archivo)
        new_predictions = classifier_tree.predict(df)
        print(new_predictions)

        point = self.influxdb_connector.point(int(new_predictions[0]),self.src_ip,self.dst_ip)
        self.influxdb_connector.write(point)

if __name__ == "__main__":


    parser = argparse.ArgumentParser(description='Data processing and writing to InfluxDB')
    parser.add_argument('-i', '--interface', type=str, help='Network interface to monitor')
    parser.add_argument('-s', '--server', type=str, help='IP address of InfluxDB')
    parser.add_argument('-p', '--port', type=str, help='Port of InfluxDB')
    args = parser.parse_args()

    if not all([args.interface, args.server, args.port]):
        parser.error('All arguments -i, -s, and -p are required')


    evento_lectura = threading.Event()
    observer = Observer()
    file_change_handler = FileChangeHandler(evento_lectura, 'file.csv')
    observer.schedule(file_change_handler, '.', recursive=False)
    observer.start()
    
    config = JsonConfig("config.json")
    influxdb_connector = InfluxDBConnector(args.server, args.port, config.field("bucket"), config.field("token"), config.field("org"), config.field("point"))
    
    writer_thread = FileWriter(args.interface,)
    reader_thread = FileReader('file.csv', evento_lectura, influxdb_connector)
    
    writer_thread.start()
    reader_thread.start()

    writer_thread.join()

    observer.stop()
    observer.join()

    print("Program finished.")
