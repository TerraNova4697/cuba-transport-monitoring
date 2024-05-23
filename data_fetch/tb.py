from tb_rest_client.rest_client_pe import RestClientPE, EntityId, DeviceId
from tb_rest_client.rest import ApiException
from dotenv import load_dotenv
from tb_device_mqtt import TBDeviceMqttClient

import logging
import os
import time
import threading

from .device import Device

load_dotenv()


CUBA_URL = os.environ.get("CUBA_URL")
CUBA_USERNAME = os.environ.get("CUBA_USERNAME")
CUBA_PASSWORD = os.environ.get("CUBA_PASSWORD")


class DataFetcher:

    def __init__(self, ts_start: int, ts_end: int, device_id: str = None):
        self.ts_start: int = ts_start
        self.ts_end: int = ts_end

    def get_timeseries(self, device, rest_client: RestClientPE):
        try:

            telemetry = rest_client.get_timeseries(
                entity_id=EntityId(id=device.id, entity_type="DEVICE"),
                keys="idling",
                start_ts=self.ts_start,
                end_ts=self.ts_end,
                limit=6000,
                order_by="ASC",
            )
            device.telemetry = telemetry.get("idling", [])

            return device

        except ApiException as e:
            logging.exception(e)

    def divide_list(self, input_list, chunk_size=200):
        if len(input_list) < chunk_size:
            return [input_list]

        # Using list comprehension to create sublists
        return [
            input_list[i : i + chunk_size]  # noqa
            for i in range(0, len(input_list), chunk_size)
        ]

    def get_timeseries_for_chunk(self, devices, rest_client):
        [self.get_timeseries(device, rest_client) for device in devices]

    def get_online_timeseries_for_devices(self, devices: list[Device]):
        with RestClientPE(base_url=CUBA_URL) as rest_client:
            try:
                rest_client.login(username=CUBA_USERNAME, password=CUBA_PASSWORD)

                device_chunks = self.divide_list(devices)

                threads = []
                for device_chunk in device_chunks:
                    t = threading.Thread(
                        target=self.get_timeseries_for_chunk,
                        args=(device_chunk, rest_client),
                    )
                    threads.append(t)
                    t.start()

                for t in threads:
                    t.join()

                return devices

            except ApiException as e:
                logging.exception(e)

    def get_devices(self):
        with RestClientPE(base_url=CUBA_URL) as rest_client:
            try:
                rest_client.login(username=CUBA_USERNAME, password=CUBA_PASSWORD)

                devices = []

                devices_result = rest_client.get_tenant_devices(500, 0, "teltonics")
                for d in devices_result.data:
                    devices.append(Device(d.name, d.id.id))

                for i in range(1, devices_result.total_pages):
                    time.sleep(1)
                    res = rest_client.get_tenant_devices(500, i, "teltonics")
                    for d in res.data:
                        devices.append(Device(d.name, d.id.id))

                return devices

            except ApiException as e:
                logging.exception(e)

    def get_device_credentials(self, device: Device, rest_client: RestClientPE):
        res = rest_client.get_device_credentials_by_device_id(
            DeviceId(device, "DEVICE")
        )
        return res.credentials_id

    def save_idlings(self, devices: list[Device]):
        with RestClientPE(base_url=CUBA_URL) as rest_client:
            try:
                rest_client.login(username=CUBA_USERNAME, password=CUBA_PASSWORD)
                for device in devices:
                    creds = self.get_device_credentials(device.id, rest_client)
                    client = TBDeviceMqttClient(CUBA_URL, username=creds)
                    client.connect()
                    client.send_telemetry(
                        [
                            {
                                "ts": int(device.date.timestamp() * 1000),
                                "values": {"dailyIdling": device.idling},
                            }
                        ]
                    )
                    client.disconnect()
            except ApiException as e:
                logging.exception(e)
