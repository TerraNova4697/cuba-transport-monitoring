"""
Collects timeseries and forms analytics records.
"""

from .data_processor import DataProcessor
from .tb import DataFetcher
from .device import Device

from datetime import datetime
import logging


class Collector:
    """Collects timeseries and forms analytics records."""

    def __init__(self, ts_start: int, ts_end: int) -> None:
        self.ts_start: int = ts_start
        self.ts_end: int = ts_end
        self.fetcher: DataFetcher = DataFetcher(ts_start, ts_end)
        self.processor: DataProcessor = DataProcessor(ts_start, ts_end)
        # Collect devices.
        self.devices: list[Device] = self.fetcher.get_devices()

    def make_record(self) -> None:
        """Make records for collected devices."""
        ts = datetime.now()

        # Get timeseries for every device.
        devices_with_online_timeseries: list[Device] = (
            self.fetcher.get_online_timeseries_for_devices(self.devices)
        )
        logging.info(f"Telemetry loaded in {datetime.now() - ts} sec.")

        # Form records.
        reports = [
            self.device_to_dict(device) for device in devices_with_online_timeseries
        ]

        # Save to DB.
        self.fetcher.save_idlings(reports)

    def device_to_dict(self, device: Device) -> dict:
        """Counts idling and forms dictionary.

        Args:
            device (Device): Given device with timeseries.

        Returns:
            dict: Dict object to save in DB.
        """
        # Count idling.
        idling = self.processor.count_idling(device.telemetry)
        device.idling = idling
        curr_date = datetime.fromtimestamp(self.ts_end / 1000)
        device.date = curr_date
        return device
