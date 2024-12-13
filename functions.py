"""
Helping functions.
"""

import argparse
import logging
import asyncio
from avl import AVL
from argparse import Namespace

from logger import logger


def parse_args() -> Namespace:
    """Parse command line and return arguments

    Returns:
        Namespace: Command line arguments.
    """

    parser = argparse.ArgumentParser(
        description="Asynchronous echo server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument_group("required arguments").add_argument(
        "--port", type=int, help="port to bind to", default=8084
    )

    parser.add_argument("--host", type=str, help="host to bind to", default="0.0.0.0")
    parser.add_argument(
        "--backlog", type=int, help="backlog for server socket", default=100
    )
    parser.add_argument("--buffer", type=int, help="read buffer size", default=1280)
    parser.add_argument(
        "--silent",
        action="store_true",
        help="do not log anything during handling connections",
    )

    return parser.parse_args()


def get_avl_packages(data: str, num: int) -> list:
    """Splits one string of messages on num parts.

    Args:
        data (str): AVL package.
        num (int): Number of messages.

    Returns:
        list: List of messages.
    """
    split_parts = []

    for i in range(0, num):
        curr = 52
        length = 60

        one_bytes = int(data[curr : curr + 2], 16)  # noqa
        if one_bytes > 0:
            length += one_bytes * 4
            curr += one_bytes * 4
        curr += 2

        two_bytes = int(data[curr : curr + 2], 16)  # noqa
        if two_bytes > 0:
            length += two_bytes * 6
            curr += two_bytes * 6
        curr += 2

        four_bytes = int(data[curr : curr + 2], 16)  # noqa
        if four_bytes > 0:
            length += four_bytes * 10
            curr += four_bytes * 10
        curr += 2

        eight_bytes = int(data[curr : curr + 2], 16)  # noqa
        if eight_bytes > 0:
            length += eight_bytes * 18
            curr += eight_bytes * 18

        split_parts.append(AVL(data[:length]))
        data = data[length:]

    return split_parts


def codec_8e_checker(codec8_packet: str) -> bool:
    """Checks if CODEC8 packet is correct.

    Args:
        codec8_packet (str): CODEC8 packer.

    Returns:
        bool: _description_
    """
    if (
        str(codec8_packet[16 : 16 + 2]).upper() != "8E"  # noqa
        and str(codec8_packet[16 : 16 + 2]).upper() != "08"  # noqa
    ):
        # logging.info()
        logging.info(str(codec8_packet[16 : 16 + 2]).upper())  # noqa
        logging.info("Invalid packet!")
        return False
    else:
        return crc16_arc(codec8_packet)


def imei_checker(hex_imei):  # IMEI checker function
    """IMEI checker function

    Args:
        hex_imei (str): IMEI

    Returns:
        bool: Is IMEI
    """
    imei_length = int(hex_imei[:4], 16)
    if imei_length != len(hex_imei[4:]) / 2:
        return False
    else:
        pass

    ascii_imei = ascii_imei_converter(hex_imei)
    logging.info(f"IMEI received = {ascii_imei}")
    if not ascii_imei.isnumeric() or len(ascii_imei) != 15:
        logging.info("Not an IMEI - is not numeric or wrong length!")
        return False
    else:
        return True


def ascii_imei_converter(hex_imei):
    return bytes.fromhex(hex_imei[4:]).decode()


def crc16_arc(data: str) -> bool:
    """Check if there are no errors in data.

    Args:
        data (str): Data.

    Returns:
        bool: _description_
    """
    data_part_length_crc = int(data[8:16], 16)
    data_part_for_crc = bytes.fromhex(data[16 : 16 + 2 * data_part_length_crc])  # noqa
    crc16_arc_from_record = data[
        16 + len(data_part_for_crc.hex()) : 24 + len(data_part_for_crc.hex())  # noqa
    ]

    crc = 0

    for byte in data_part_for_crc:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1

    if crc16_arc_from_record.upper() == crc.to_bytes(4, byteorder="big").hex().upper():
        print("CRC check passed!")
        print(f"Record length: {len(data)} characters // {int(len(data)/2)} bytes")
        return True
    else:
        print("CRC check Failed!")
        return False


def create_handler(buff_size: int, mapped_transport: dict) -> asyncio.coroutine:
    """Generates TCP handler.

    Args:
        buff_size (int): Size of message.
        mapped_transport (dict): Registered transports.

    Returns:
        asyncio.coroutine: Coroutine. Will handle every request.
    """

    async def handler(reader, writer):
        while True:
            try:

                # Read coming data.
                try:
                    chunk = await reader.read(buff_size)
                    ip, port = writer.get_extra_info('peername')
                    logger.debug(f"{ip=}; {port=}")
                except asyncio.TimeoutError:
                    writer.close()
                    logger.info("Client timeout")
                    await writer.wait_closed()
                    return

                # Close connection if empty data
                if not chunk:
                    writer.close()
                    logger.info("Client connection closed (empty message)")
                    await writer.wait_closed()
                    return

                logger.info(f"Received: {chunk}")

                # Return 01 bytes if received data is preambule and IMEI is registered.
                # Close connection if the vehicle is not registered.
                try:
                    if imei_checker(chunk.hex()):
                        imei = chunk[2:].decode()

                        if mapped_transport.get(imei):
                            logger.info(f"decoded imei, {imei}")
                            logger.info(
                                "Send: {!r}".format((1).to_bytes(1, byteorder="big"))
                            )
                            writer.write((1).to_bytes(1, byteorder="big"))

                        else:
                            writer.close()
                            logger.warning(
                                f"Unregistered device {imei} from {writer.get_extra_info('peername')}"
                            )
                            await writer.wait_closed()
                            return

                except UnicodeDecodeError:
                    pass
                except IndexError:
                    writer.close()
                    logger.info("Unsupported data")
                    await writer.wait_closed()
                    return

                # Parse data and send telemetry
                try:
                    avl = chunk.hex()

                    # Check if CODEC8 is correct.
                    if codec_8e_checker(chunk.hex().replace(" ", "")):

                        # Get length of the package and number of AVL packages.
                        length = int(avl[8:16], 16)  # noqa
                        number_of_data = int(avl[18:20], 16)
                        logger.info(f"num of data {number_of_data}; length: {length}")

                        # Split AVL packages and send telemetry.
                        avl_packages = get_avl_packages(avl[20:-10], number_of_data)
                        mapped_transport[imei].send_telemetry(avl_packages)

                        # Send response that message was acknoledged.
                        response = (number_of_data).to_bytes(4, byteorder="big")
                        logger.info(f"send response: {response}")
                        writer.write(response)
                except (AttributeError, IndexError):
                    writer.close()
                    logger.info("Unsupported data")
                    logger.info("Connection closed")
                    await writer.wait_closed()
                    return

                # writer.write(chunk)

                # Uncomment if you need http response
                # Note: We don't close connection in such case so be sure that your clients sends keep-alive header
                # writer.write(f"HTTP/1.1 200 OK\r\nContent-Length:0\r\n\r\n".encode())

                await writer.drain()
            except ConnectionResetError as e:
                logger.info(f"ConnectionResetError: {e}")
                writer.close()
                logger.info("Connection closed")
                await writer.wait_closed()
                return

    return handler
