import asyncio
import logging

from functions import create_handler

from functions import parse_args
from config import transports as transports_config, CUBA_URL
from transport import Transport


log_fh = logging.FileHandler("transport-monitoring.log")
_ = logging.basicConfig(
    format="%(asctime)s - %(name)s - %(lineno)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
    filename="transport-monitoring.log",
)
logger = logging.getLogger()


async def start_server(args, mapped_transport):
    server = await asyncio.start_server(
        create_handler(args.buffer, mapped_transport),
        host=args.host,
        port=args.port,
        backlog=args.backlog,
    )

    async with server:
        print(f"Serving on {args.host}:{args.port}...")
        await server.serve_forever()


def main():
    # Load, instanciate transport && map to its IMEIs
    transports = [
        Transport(
            imei=t["imei"], username=t["username"], items=t["items"], url=CUBA_URL
        )
        for t in transports_config
    ]
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
