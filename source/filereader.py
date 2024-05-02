from .modelprocessor import ModelProcessor
import threading
import time

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
                for line in file:
                    if not first_line:  
                        process = ModelProcessor(self.influxdb_connector, line)
                        print(line.strip()) 
                        process.process_model()
                        time.sleep(0.5)
                    first_line = False
                last_position = file.tell()
                self.event.clear()