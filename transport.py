import logging

from tb_gateway_mqtt import TBGatewayMqttClient


logger = logging.getLogger()


class Transport:

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

    def connect(self):
        self.gateway.gw_connect_device(self.name, "teltonics")

    def send_telemetry(self, packs):

        data = []
        for pack in packs:
            parsed = pack.form_telemetry()
            data.append(parsed)

            # telemetry = {"ts": parsed.get("timestamp"), "values": parsed}
        result = self.gateway.gw_send_telemetry(self.name, data)
        logger.info(f"Sent telemetry. Success: {result}, Data: {data}")

    def __repr__(self):
        return f"Transport: IMEI: {self.imei}; Device token: {self.name}"
