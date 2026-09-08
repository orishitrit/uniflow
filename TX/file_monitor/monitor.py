import argparse
import os
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from pathlib import Path
from TX.file_monitor.chunker import file_chunking
import time
from TX.file_monitor.chunk_dispatcher import ChunkDispatcher
import asyncio
TEN_MB = 10 * 1024 * 1024  # 10 MB in bytes


class FileEventHandler(FileSystemEventHandler):
    def __init__(self, loop: asyncio.AbstractEventLoop, dispatcher: ChunkDispatcher):
        super().__init__()
        self.loop = loop
        self.dispatcher = dispatcher
        
    def on_created(self, event):
        if event.is_directory:
            return

        print(f"File created: {event.src_path}")
        asyncio.run_coroutine_threadsafe(
            self.handle_file(Path(event.src_path)),
            self.loop
        )

    async def handle_file(self, file_path: Path):
        await self.dispatcher.open_gates.wait()
        
        try:
            file_size = file_path.stat().st_size
        except OSError:
            return

        if file_path.stat().st_size > TEN_MB:
            print(f"File {file_path} exceeds 10MB, chunking...")
            self.dispatcher.drain()
            
            try:
                await self.dispatcher.dispatch_file(file_path)
            
            finally:
                file_path.unlink(missing_ok=True)
                
        else:
            print(f"File {file_path} is under 10MB, dispatching directly...")
            await self.dispatcher.dispatch_file(file_path)

        
def start_monitoring(path_to_watch):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    event_handler = FileEventHandler(loop, ChunkDispatcher())
    observer = Observer()
    observer.schedule(event_handler, path=path_to_watch, recursive=True)
    observer.start()

    print(f"Monitoring started on: {path_to_watch}")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
        loop.stop()
        loop.close()
    

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


