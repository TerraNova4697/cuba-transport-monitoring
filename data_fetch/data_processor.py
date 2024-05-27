import json

# from datetime import datetime


class DataProcessor:

    def __init__(self, ts_start: int, ts_end: int, data: list = None):
        self.data: dict | None = None
        self.ts_start: int = ts_start
        self.ts_end: int = ts_end
        self.uptime_downtime_percent: dict | None = 0
        self.total_downtime_duration_sec: int | None = 0
        self.total_idling_sec: int | None = 0

    def count_idling(self, data: list[dict]) -> tuple:
        """Counts downtime in milliseconds for given period

        Args:
            data (list[dict]): Timeseries

        Returns:
            total_duration int: Downtime in seconds
        """

        self.total_idling_sec = 0
        idling_pointer = None

        if not data:
            return self.total_idling_sec

        if data[-1]["value"] == "0":
            total_duration_idling = 0
        else:
            total_duration_idling = self.ts_end - data[-1]["ts"]

        for i in range(len(data) - 1, -1, -1):

            if data[i]["value"] == "1" and idling_pointer is None:
                idling_pointer = i

            if data[i]["value"] == "0" and idling_pointer is not None:
                delta = data[idling_pointer]["ts"] - data[i]["ts"]
                total_duration_idling += delta
                idling_pointer = None

        if idling_pointer:
            delta = data[idling_pointer]["ts"] - data[0]["ts"]
            total_duration_idling += delta

        if data[0]["value"] == "1":
            total_duration_idling += data[0]["ts"] - self.ts_start

        self.total_idling_sec = round(total_duration_idling / 1000)
        return self.total_idling_sec

    def test_count_downtime_delta(self) -> int:
        """Counts downtime in milliseconds for given period

        Args:
            data (list[dict]): Timeseries

        Returns:
            total_duration int: Downtime in milliseconds
        """
        with open("telemetry.json", "r") as file:
            obj = json.load(file)
            data = obj["online"]
            data = data[::-1]
        total_time = self.ts_end - data[0]["ts"]
        start_pointer = None

        if data[-1]["value"] == "0":
            total_duration_offline = self.ts_end - data[-1]["ts"]
        else:
            total_duration_offline = 0

        for i in range(len(data) - 1, -1, -1):
            if data[i]["value"] == "0" and start_pointer is None:
                start_pointer = i

            if data[i]["value"] == "1" and start_pointer is not None:
                delta = data[start_pointer]["ts"] - data[i]["ts"]
                total_duration_offline += delta
                start_pointer = None

        if start_pointer and data[start_pointer]["value"] == "0":
            delta = data[start_pointer]["ts"] - data[0]["ts"]
            total_duration_offline += delta

        self.total_downtime_duration = total_duration_offline
        return (
            round(total_duration_offline / 1000),
            round(total_duration_offline / total_time * 100, 5),
            round((total_time - total_duration_offline) / 1000),
            round((total_time - total_duration_offline) / total_time * 100, 5),
        )

    def process_uptime_downtime_percent(self, data):
        total_time = self.data[-1]["ts"] - self.data[0]["ts"]
        start_pointer = None

        if self.data[-1]["value"] == "0":
            total_duration = self.ts_end - self.data[-1]["ts"]
        else:
            total_duration = 0

        for i in range(len(self.data) - 1, -1, -1):
            if self.data[i]["value"] == "0" and start_pointer is None:
                start_pointer = i

            if self.data[i]["value"] == "1" and start_pointer is not None:
                delta = self.data[start_pointer]["ts"] - self.data[i]["ts"]
                total_duration += delta
                start_pointer = None

        self.uptime_downtime_percent = {
            "uptime_percent": round(
                (total_time - total_duration) / total_time * 100, 5
            ),
            "downtime_percent": round(total_duration / total_time * 100, 5),
        }

        return self.uptime_downtime_percent

    def get_uptime_downtime_percent(self):
        return self.uptime_downtime_percent
