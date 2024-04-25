import logging

from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo


logger = logging.getLogger()


class Transport:

    def __init__(self, imei, username, items, url):
        self.imei = imei
        self.username = username
        self.items = items
        self.client: TBDeviceMqttClient | None = None
        self.url = url
        self.connect()

    def connect(self):
        client = TBDeviceMqttClient(host=self.url, username=self.username)
        client.connect()
        self.client = client

    def is_device_connected(self):
        if not self.client:
            return False
        return self.client.is_connected()

    def send_telemetry(self, packs):
        if not self.is_device_connected():
            self.connect()

        data = []
        for pack in packs:
            parsed = pack.form_telemetry()
            data.append(parsed)

            # telemetry = {"ts": parsed.get("timestamp"), "values": parsed}
        result = self.client.send_telemetry(data)
        success = result.get() == TBPublishInfo.TB_ERR_SUCCESS
        logger.info(f"Sent telemetry. Success: {success}, Data: {data}")

    def __repr__(self):
        return f"Transport: IMEI: {self.imei}; Device token: {self.username}"
