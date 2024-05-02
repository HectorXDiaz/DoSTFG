from watchdog.events import FileSystemEventHandler

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, event, file_path):
        super().__init__()
        self.event = event
        self.file_path = file_path

    def on_modified(self, event):
        if event.src_path.endswith(self.file_path):
            self.event.set()