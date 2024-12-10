"""
Program entry module.
"""

import asyncio
import logging

from functions import create_handler

from functions import parse_args
from config import CUBA_URL, TB_GATEWAY_TOKEN
from transport import Transport
from database import get_all_transport
from argparse import Namespace

from tb_gateway_mqtt import TBGatewayMqttClient


log_fh = logging.FileHandler("transport-monitoring.log")
_ = logging.basicConfig(
    format="%(asctime)s - %(name)s - %(lineno)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
    filename="transport-monitoring.log",
)
logger = logging.getLogger()


async def start_server(args: Namespace, mapped_transport: dict) -> None:
    """Starts server and passes callback function.

    Args:
        args (Namespace): Command list arguments.
        mapped_transport (dict): Transports dictionary.
    """

    # Create server.
    server = await asyncio.start_server(
        create_handler(args.buffer, mapped_transport),
        host=args.host,
        port=args.port,
        backlog=args.backlog,
    )

    # Run server forever.
    async with server:
        print(f"Serving on {args.host}:{args.port}...")
        await server.serve_forever()


def main() -> None:
    """Programm entry point."""

    # Connecting to Gateway
    gateway = TBGatewayMqttClient(
        CUBA_URL,
        1883,
        TB_GATEWAY_TOKEN,
    )
    gateway.connect()

    # Load, instanciate transport && map to its IMEIs
    transports = [
        Transport(
            imei=t.imei,
            name=t.name,
            url=CUBA_URL,
            gateway=gateway,
        )
        for t in get_all_transport()
    ]
    logger.info(f"{transports}")
    mapped_imeis = {t.imei: t for t in transports}

    # Parse command line arguments
    args = parse_args()

    # Start server
    try:
        asyncio.run(start_server(args, mapped_imeis))
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()
