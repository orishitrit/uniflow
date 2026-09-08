from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class RouterConfig:
    listen_ports: List[int]
    target_ports: List[int]
    loss_rate: float
    flip_rate: float
    misroute_rate: float
    target_host: str
    socket_buffer_size: int = 64 * 1024  # 64KB

DEFAULT_LISTEN_PORTS = [8001, 8002, 8003]
DEFAULT_TARGET_PORTS = [9001, 9002, 9003]