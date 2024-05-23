from .data_processor import DataProcessor
from .tb import DataFetcher
from .device import Device

# from db.database import save_reports

from datetime import datetime
import logging


class Collector:

    def __init__(self, ts_start, ts_end):
        self.ts_start: int = ts_start
        self.ts_end: int = ts_end
        self.fetcher: DataFetcher = DataFetcher(ts_start, ts_end)
        self.processor: DataProcessor = DataProcessor(ts_start, ts_end)
        self.devices: list[Device] = self.fetcher.get_devices()

    def make_record(self):
        ts = datetime.now()

        devices_with_online_timeseries: list[Device] = (
            self.fetcher.get_online_timeseries_for_devices(self.devices)
        )
        logging.info(f"Telemetry loaded in {datetime.now() - ts} sec.")

        reports = [
            self.device_to_dict(device) for device in devices_with_online_timeseries
        ]

        for r in reports:
            print(r.idling)

        self.fetcher.save_idlings(reports)

    def device_to_dict(self, device: Device) -> dict:
        idling = self.processor.count_idling(device.telemetry)
        print(idling)
        device.idling = idling
        curr_date = datetime.fromtimestamp(self.ts_end / 1000)
        device.date = curr_date
        return device
