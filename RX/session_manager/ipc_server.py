import os
import selectors
import socket
import struct
from typing import Callable, Dict, List, Optional


class IPCServer:
    def __init__(self, socket_paths: List[str]):
        self.selector = selectors.DefaultSelector()
        self.socket_paths = socket_paths
        self.buffers: Dict[int, bytearray] = {}
        self.observers: List[Callable[[bytes], None]] = []
        self.tick_callback: Optional[Callable[[], None]] = None

        for path in self.socket_paths:
            if os.path.exists(path):
                os.remove(path)
            server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            server_sock.bind(path)
            server_sock.listen()
            server_sock.setblocking(False)
            self.selector.register(server_sock, selectors.EVENT_READ, self._accept)

    def register_observer(self, callback: Callable[[bytes], None]) -> None:
        self.observers.append(callback)

    def register_tick_handler(self, callback: Callable[[], None]) -> None:
        self.tick_callback = callback

    def _notify(self, message: bytes) -> None:
        for observer in self.observers:
            observer(message)

    def _accept(self, server_sock: socket.socket) -> None:
        conn, _ = server_sock.accept()
        conn.setblocking(False)
        self.buffers[conn.fileno()] = bytearray()
        self.selector.register(conn, selectors.EVENT_READ, self._read)

    def _read(self, conn: socket.socket) -> None:
        fd = conn.fileno()
        try:
            chunk = conn.recv(65536)
            if not chunk:
                self._close(conn)
                return

            buf = self.buffers[fd]
            buf.extend(chunk)

            while len(buf) >= 4:
                msg_len = struct.unpack(">I", buf[:4])[0]
                if len(buf) < 4 + msg_len:
                    break

                msg_bytes = bytes(buf[4 : 4 + msg_len])
                del buf[: 4 + msg_len]
                self._notify(msg_bytes)

        except (ConnectionResetError, BrokenPipeError):
            self._close(conn)

    def _close(self, conn: socket.socket) -> None:
        try:
            self.selector.unregister(conn)
        except (KeyError, ValueError):
            pass
        self.buffers.pop(conn.fileno(), None)
        try:
            conn.close()
        except OSError:
            pass

    def start(self) -> None:
        try:
            while True:
                events = self.selector.select(timeout=1.0)
                for key, _ in events:
                    callback = key.data
                    callback(key.fileobj)

                if self.tick_callback:
                    self.tick_callback()
        finally:
            self.selector.close()