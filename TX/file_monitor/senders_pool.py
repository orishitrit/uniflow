import asyncio
import os
from TX.file_monitor.chunk_dispatcher import ChunkDispatcher

SOCKET_PATH = "/tmp/file_monitor.sock"
dispatcher = ChunkDispatcher()

async def register_worker(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    dispatcher.setWorkerReady(writer)
    print(f"Worker registered.")

async def handle_workers():
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    server = await asyncio.start_unix_server(register_worker, SOCKET_PATH)
    print(f"Worker pool server started at {SOCKET_PATH}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(handle_workers())
