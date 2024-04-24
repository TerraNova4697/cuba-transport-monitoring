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

        # 0000018e9d98e1d0      | timestamp                | [0:16]
        # 00                    | priority                 | [16:18]
        # 2a9e9581              | longitude                | [18:26]
        # 1e774ce5              | latitude                 | [26:34]
        # 016f                  | altitude                 | [34:38]
        # 0000                  | angle                    | [38:42]
        # 0d                    | satellites               | [42:44]
        # 0000                  | speed                    | [44:48]
        #
        # 00                    | event IO ID              | [48:50]
        # 0e                    | num of total events      | [50:52]
        # 07                    | num of 1 byte events     | [52:54]
        # ef00 f000 1505 c800 4501 0100 0200               | [54:54 + 1_bytes_total * 4]
        #
        # 05                    | num of 2 byte events
        # b5000b 4231a0 cd0b05 431016 440000
        #
        # 02                    | num of 4 byte events
        # f100009cf1 10001b6bd8
        #
        # 00                    | num of 8 byte events
        data = []
        for pack in packs:
            parsed = pack.form_telemetry(self.items)
            data.append(parsed)

            # telemetry = {"ts": parsed.get("timestamp"), "values": parsed}
        result = self.client.send_telemetry(data)
        success = result.get() == TBPublishInfo.TB_ERR_SUCCESS
        logger.info(f"Sent telemetry. Success: {success}, Data: {data}")

    def parse_avl_package(self, package):
        data = package.form_telemetry(self.items)

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
