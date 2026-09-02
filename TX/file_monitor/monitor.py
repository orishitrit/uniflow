import argparse
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from pathlib import Path
from TX.file_monitor.chunker import file_chunking
import time

class FileEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        print(f"File created: {event.src_path}")
        file_chunking(Path(event.src_path))

def start_monitoring(path_to_watch):
    event_handler = FileEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path_to_watch, recursive=True)
    observer.start()

    print(f"Monitoring started on: {path_to_watch}")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, required=True, help='Path to monitor')

    args = parser.parse_args()
    path_to_monitor = Path(args.path)

    if path_to_monitor.is_dir():
        start_monitoring(path_to_monitor)
    else:
        print(f"The provided path '{path_to_monitor}' is not a directory.")
        return


if __name__ == "__main__":
    main()


