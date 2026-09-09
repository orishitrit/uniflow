import asyncio
import TX.file_monitor.chunker as chunker
import itertools
import struct

class ChunkDispatcher:
    def __init__(self):
        self.ready_workers = asyncio.Queue()
        self.busy_workers = set()

        self.open_gates = asyncio.Event()
        self.open_gates.set()

        self.all_ready = asyncio.Event()
        self.all_ready.clear()

    def open(self):
        self.open_gates.set()
        print("gates are open.")

    def close(self):
        self.open_gates.clear()
        print("gates are closed.")

    def setWorkerReady(self, worker):
        self.ready_workers.put_nowait(worker)
        print(f"Worker {worker} registered successfully.")
        if not self.busy_workers:
            self.all_ready.set()

        print("\nHELLO")
        print(list(self.ready_workers._queue))
        print("HELLOO")
        

    async def dispatch_chunk(self, chunk, worker):
        payload = chunk.SerializeToString()
        # אריזת 4 בייטים של אורך ב-Big Endian (כמו htonl)
        header = struct.pack('>I', len(payload))
    
        worker.write(header + payload)
        if hasattr(worker, 'drain'):
            await worker.drain()

    async def dispatch_file(self, file_path):
        if not self.open_gates.is_set():
            print("Drain is active. Waiting for all workers to be ready...")
            await self.all_ready.wait()
            print("All workers are ready. Resuming dispatching.")

            while not self.ready_workers.empty():
                worker = self.ready_workers.get_nowait()
                self.busy_workers.add(worker)

            self.all_ready.clear()

            worker_cycle = itertools.cycle(list(self.busy_workers))
            
            try:
                for chunk in chunker.file_chunking(file_path):
                    while self.busy_workers:
                        current_worker = next(worker_cycle)

                        try:
                            await self.dispatch_chunk(chunk, current_worker)
                            break

                        except (ConnectionResetError, BrokenPipeError):
                                    print("Worker disconnected during dispatch. Dropping it.")
                                    self.busy_workers.remove(current_worker)
                                    current_worker.close()

                                    if self.busy_workers:
                                        worker_cycle = itertools.cycle(list(self.busy_workers))
                                    else:
                                        raise RuntimeError("All workers disconnected during drain.")

            finally:
                while self.busy_workers:
                    worker = self.busy_workers.pop()
                    self.ready_workers.put_nowait(worker)

                if not self.ready_workers.empty():
                    self.all_ready.set()

                self.open_gates.set()

        else:
            print("Dispatching file without drain.")
            print("\nHELLO1")
            print(list(self.ready_workers._queue))
            print("HELLO2")
            worker = await self.ready_workers.get()
            print("found worker.")

            self.all_ready.clear()
            self.busy_workers.add(worker)

            try:
                print("chunkkking file...")
                print(file_path.stat().st_size)         
                for chunk in chunker.file_chunking(file_path):
                    print("Dispatching chunk to worker.\n")
                    print(chunk)
                    await self.dispatch_chunk(chunk, worker)
                    print("done it!")

                self.busy_workers.remove(worker)
                self.ready_workers.put_nowait(worker)

            except (ConnectionResetError, BrokenPipeError):
                print("Worker disconnected during dispatch. Dropping it.")
                self.busy_workers.remove(worker)
                worker.close()

            finally:
                if(not self.busy_workers and not self.ready_workers.empty()):
                    self.all_ready.set()

    