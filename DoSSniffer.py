import threading
from watchdog.observers import Observer
import argparse

from source.filechangehandler import FileChangeHandler
from source.jsonconfig import JsonConfig
from source.filereader import FileReader
from source.filewriter import FileWriter
from source.influxdbconnector import InfluxDBConnector

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Data processing and writing to InfluxDB')
    parser.add_argument('-i', '--interface', type=str, help='Network interface to monitor')
    parser.add_argument('-s', '--server', type=str, help='IP address of InfluxDB')
    parser.add_argument('-p', '--port', type=str, help='Port of InfluxDB')
    args = parser.parse_args()

    if not all([args.interface, args.server, args.port]):
        parser.error('All arguments -i, -s, and -p are required')


    read_event = threading.Event()
    observer = Observer()
    file_change_handler = FileChangeHandler(read_event, 'file.csv')
    observer.schedule(file_change_handler, '.', recursive=False)
    observer.start()
    
    config = JsonConfig("config.json")
    influxdb_connector = InfluxDBConnector(args.server, args.port, config.field("bucket"), config.field("token"), config.field("org"), config.field("point"))
    
    writer_thread = FileWriter(args.interface,)
    reader_thread = FileReader('file.csv', read_event, influxdb_connector)
    
    writer_thread.start()
    reader_thread.start()

    writer_thread.join()

    observer.stop()
    observer.join()

    print("Program finished.")
