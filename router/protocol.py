import asyncio
import random
import socket
from router.config import RouterConfig

class RouterProtocol(asyncio.DatagramProtocol):
    def __init__(self, channel_id: int, config: RouterConfig):
        self.channel_id = channel_id
        self.config = config
        self.transport: asyncio.DatagramTransport | None = None

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        self.transport = transport
        sock = self.transport.get_extra_info("socket")
        if sock is not None:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.config.socket_buffer_size)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.config.socket_buffer_size)

    def datagram_received(self, data: bytes, addr) -> None:
        if random.random() < self.config.loss_rate:
            return

        payload = bytearray(data)
        if random.random() < self.config.flip_rate and len(payload) > 0:
            byte_idx = random.randint(0, len(payload) - 1)
            bit_idx = random.randint(0, 7)
            payload[byte_idx] ^= 1 << bit_idx

        destination_port = self.config.target_ports[self.channel_id]
        if random.random() < self.config.misroute_rate:
            other_ports = [
                p for i, p in enumerate(self.config.target_ports) if i != self.channel_id
            ]
            if other_ports:
                destination_port = random.choice(other_ports)

        # שליחה ישירה ללא השהיה
        if self.transport and not self.transport.is_closing():
            self.transport.sendto(bytes(payload), (self.config.target_host, destination_port))