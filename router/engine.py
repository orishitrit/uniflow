import asyncio
from typing import List
from router.config import RouterConfig
from router.protocol import RouterProtocol

class RouterEngine:
    def __init__(self, config: RouterConfig):
        self.config = config
        self.transports: List[asyncio.DatagramTransport] = []

    async def start(self) -> None:
        loop = asyncio.get_running_loop()

        for idx, listen_port in enumerate(self.config.listen_ports):
            transport, _ = await loop.create_datagram_endpoint(
                lambda ch=idx: RouterProtocol(channel_id=ch, config=self.config),
                local_addr=("0.0.0.0", listen_port),
            )
            self.transports.append(transport)

    def stop(self) -> None:
        for transport in self.transports:
            if not transport.is_closing():
                transport.close()
        self.transports.clear()