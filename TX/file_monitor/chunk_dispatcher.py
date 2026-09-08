import asyncio
from TX.file_monitor.chunker import file_chunking
import itertools

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
        print(f"Worker {worker} is ready.")
        if not self.busy_workers:
            self.all_ready.set()

    async def dispatch_chunk(self, chunk, worker):
        worker.write(chunk.SerializeToString())
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
                for chunk in file_chunking(file_path):
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
            worker = await self.ready_workers.get()

            self.all_ready.clear()
            self.busy_workers.add(worker)

            try:            
                for chunk in file_chunking(file_path):
                    await self.dispatch_chunk(chunk, worker)

                self.busy_workers.remove(worker)
                self.ready_workers.put_nowait(worker)

            except (ConnectionResetError, BrokenPipeError):
                print("Worker disconnected during dispatch. Dropping it.")
                self.busy_workers.remove(worker)
                worker.close()

            finally:
                if(not self.busy_workers and not self.ready_workers.empty()):
                    self.all_ready.set()

    