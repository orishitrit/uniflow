import argparse
import asyncio
import sys
from router.config import RouterConfig, DEFAULT_LISTEN_PORTS, DEFAULT_TARGET_PORTS
from router.engine import RouterEngine

def parse_args() -> RouterConfig:
    parser = argparse.ArgumentParser(description="Uniflow Router Simulator")
    parser.add_argument(
        "--loss",
        type=float,
        default=0.05,
        help="Probability of packet loss (0.0 to 1.0)",
    )
    parser.add_argument(
        "--flip",
        type=float,
        default=0.02,
        help="Probability of bit flips (0.0 to 1.0)",
    )
    parser.add_argument(
        "--misroute",
        type=float,
        default=0.10,
        help="Probability of packet misrouting (0.0 to 1.0)",
    )
    parser.add_argument(
        "--target-host",
        type=str,
        default="127.0.0.1",
        help="Destination host IP for receivers",
    )
    args = parser.parse_args()

    return RouterConfig(
        listen_ports=DEFAULT_LISTEN_PORTS,
        target_ports=DEFAULT_TARGET_PORTS,
        loss_rate=args.loss,
        flip_rate=args.flip,
        misroute_rate=args.misroute,
        target_host=args.target_host,
    )


async def main() -> None:
    config = parse_args()
    engine = RouterEngine(config)
    await engine.start()

    try:
        await asyncio.Future()
    except (asyncio.CancelledError, KeyboardInterrupt):
        engine.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)