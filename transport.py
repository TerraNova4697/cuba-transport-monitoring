import logging

from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo


logger = logging.getLogger()


class Transport:

    def __init__(self, imei, username, url):
        self.imei = imei
        self.username = username
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
        for pack in packs:
            parsed = self.parse_avl_package(pack)

            telemetry = {"ts": parsed.get("timestamp"), "values": parsed}
            result = self.client.send_telemetry(telemetry)
            success = result.get() == TBPublishInfo.TB_ERR_SUCCESS
            logger.info(f"Sent telemetry. Success: {success}, Data: {telemetry}")

    def parse_avl_package(self, package):
        data = dict()

        logger.info(package)
        data["timestamp"] = int(package[0:16], 16)
        data["priority"] = int(package[16:18], 16)
        if package[18:24] != "00000000":
            data["longitude"] = int(package[18:26], 16) / 10000000
        if package[26:34] != "00000000":
            data["latitude"] = int(package[26:34], 16) / 10000000
        # if package[34:38]:
        #     data['altitude'] = int(package[34:38], 16)
        # if package[38:42]:
        #     data['angle'] = int(package[38:42], 16)
        # if package[42:44]:
        #     data['satellites'] = int(package[42:44], 16)
        if package[44:48]:
            data["speed"] = int(package[44:48], 16)
        if package[54:56] == "ef":
            data["button"] = int(package[56:58], 16)

        return data

    def __repr__(self):
        return f"Transport: IMEI: {self.imei}; Device token: {self.username}"
