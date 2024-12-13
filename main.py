"""
Program entry module.
"""

import asyncio

from configs.settings import Settings
from database.queries.transport_orm import TransportOrm
from functions import create_handler

from functions import parse_args
from transport import Transport
from argparse import Namespace

from tb_gateway_mqtt import TBGatewayMqttClient

from logger import logger


settings = Settings()


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
    """Program entry point."""

    # Connecting to Gateway
    gateway = TBGatewayMqttClient(
        settings.cuba_url,
        1883,
        settings.cuba_gateway_token,
    )
    gateway.connect()

    # Load, instantiate transport && map to its IMEIs
    transports = [
        Transport(
            imei=t.imei,
            name=t.name,
            url=settings.cuba_url,
            gateway=gateway,
        )
        for t in TransportOrm.get_all_transport()
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
