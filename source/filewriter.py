import threading
import subprocess

class FileWriter(threading.Thread):
    def __init__(self, interface):
        super().__init__()
        self.interface = interface
    def run(self):
        try:
            subprocess.run("sudo poetry run cicflowmeter -i " + self.interface + " -c file.csv", shell=True)
        except OSError as e:
            print("Error: The specified network interface does not exist.")