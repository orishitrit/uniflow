import asyncio
import os
from TX.file_monitor.chunk_dispatcher import ChunkDispatcher

SOCKET_PATH = "/tmp/file_monitor.sock"

async def register_worker(reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
                          chunkDispatcher: ChunkDispatcher):
    chunkDispatcher.setWorkerReady(writer)
    print(f"Worker registered.")

async def handle_workers(chunkDispatcher : ChunkDispatcher):
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    server = await asyncio.start_unix_server(lambda r, w: register_worker(r, w, chunkDispatcher), SOCKET_PATH)
    print(f"Worker pool server started at {SOCKET_PATH}")

    async with server:
        await server.serve_forever()

