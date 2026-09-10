import argparse
from pathlib import Path
import asyncio
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from TX.file_monitor.chunker import file_chunking
from TX.file_monitor.chunk_dispatcher import ChunkDispatcher
from TX.file_monitor.senders_pool import handle_workers

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

        if file_size > TEN_MB:
            print(f"File {file_path} exceeds 10MB, chunking...")
            self.dispatcher.drain()

            try:
                await self.dispatcher.dispatch_file(file_path)
            finally:
                file_path.unlink(missing_ok=True)
        else:
            print(f"File {file_path} is under 10MB, dispatching directly...")
            await self.dispatcher.dispatch_file(file_path)


async def start_monitoring(path_to_watch: Path, chunkDispatcher: ChunkDispatcher):
    loop = asyncio.get_running_loop()
    event_handler = FileEventHandler(loop, chunkDispatcher)
    observer = Observer()
    observer.schedule(event_handler, path=str(path_to_watch), recursive=True)
    observer.start()

    print(f"Monitoring started on: {path_to_watch}")

    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        observer.stop()
        observer.join()


async def asyn_main(path_to_monitor: Path, chunkDispatcher: ChunkDispatcher):
    server_task = asyncio.create_task(handle_workers(chunkDispatcher))
    monitor_task = asyncio.create_task(start_monitoring(path_to_monitor, chunkDispatcher))

    await asyncio.gather(server_task, monitor_task)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, required=True, help='Path to monitor')

    args = parser.parse_args()
    path_to_monitor = Path(args.path)
    chunkDispatcher = ChunkDispatcher()

    if not path_to_monitor.is_dir():
        print(f"The provided path '{path_to_monitor}' is not a directory.")
        return

    try:
        asyncio.run(asyn_main(path_to_monitor, chunkDispatcher))
    except KeyboardInterrupt:
        print("\nStopping...")


if __name__ == "__main__":
    main()