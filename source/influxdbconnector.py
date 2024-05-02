import influxdb_client
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS
import socket

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