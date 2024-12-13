"""
Transport representation.
"""

import logging

from tb_gateway_mqtt import TBGatewayMqttClient

from logger import logger


class Transport:
    """Transport representation."""

    def __init__(
        self,
        imei: str,
        name: str,
        url: str,
        gateway: TBGatewayMqttClient,
    ):
        self.imei = imei
        self.name = name
        self.url = url
        self.gateway: TBGatewayMqttClient = gateway
        self.connect()

    def connect(self) -> None:
        """Connect device to platform."""
        self.gateway.gw_connect_device(self.name, "Teltonika Transport")

    def send_telemetry(self, packs: list[str]) -> None:
        """Send given messages on platform.

        Args:
            packs (list): Messages
        """

        # Form telemetry.
        data = []
        for pack in packs:
            parsed = pack.form_telemetry()
            data.append(parsed)

        # Send telemetry.
        result = self.gateway.gw_send_telemetry(self.name, data)
        logger.info(f"Sent telemetry. Success: {result}, Data: {data}")

    def __repr__(self):
        return f"Transport: IMEI: {self.imei}; Device token: {self.name}"
