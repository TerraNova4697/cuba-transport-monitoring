class AVL:

    verbose_names = {
        "ef": "ignition",
        "f0": "movement",
        "15": "gsmSignal",
        "c8": "sleepMode",
        "45": "gnssStatus",
        "01": "digitalInput1",
        "02": "digitalInput2",
        "03": "digitalInput3",
        "b3": "digitalOutput1",
        "b4": "digitalOutput2",
        "09": "analogInput1",
        "06": "analogInput2",
        "b5": "gnssPdop",
        "b6": "gnssHdop",
        "42": "externalVoltage",
        "cd": "gsmCellID",
        "43": "batteryVoltage",
        "44": "batteryCurrent",
        "f1": "activeGsmOperator",
        "10": "totalOdometer",
        "c7": "tripOdometer",
    }

    def __init__(self, data):
        self.data = data
        self.telemetry = {
            "ts": int(data[0:16], 16),
            "values": {
                "priority": int(data[16:18], 16),
                "latitude": int(data[26:34], 16) / 10000000,
                "longitude": int(data[18:26], 16) / 10000000,
                "altitude": int(data[34:38], 16),
                "angle": int(data[38:42], 16),
                "satellites": int(data[42:44], 16),
                "speed": int(data[44:48], 16),
                "event_io_id": int(data[48:50], 16),
                "total_events": int(data[50:52], 16),
            },
        }
        self.byte_1_events_total = None
        self.byte_1_events = None
        self.byte_2_events_total = None
        self.byte_2_events = None
        self.byte_4_events_total = None
        self.byte_4_events = None
        self.byte_8_events_total = None
        self.byte_8_events = None
        self.registered_events = {}
        self.parse_events()

    def parse_events(self):
        self.byte_1_events_total = int(self.data[52:54], 16)
        if self.byte_1_events_total > 1:
            self.byte_1_events = self.data[
                54 : 54 + (self.byte_1_events_total * 4)  # noqa
            ]
            remaining = self.data[54 + (self.byte_1_events_total * 4) :]  # noqa
        else:
            self.byte_1_events = ""
            remaining = self.data[56:]

        self.byte_2_events_total = int(remaining[0:2], 16)
        if self.byte_2_events_total > 1:
            self.byte_2_events = remaining[2 : 2 + self.byte_2_events_total * 6]  # noqa
            remaining = remaining[2 + self.byte_2_events_total * 6 :]  # noqa
        else:
            self.byte_2_events = ""
            remaining = remaining[2:]

        self.byte_4_events_total = int(remaining[0:2], 16)
        if self.byte_4_events_total > 1:
            self.byte_4_events = remaining[
                2 : 2 + self.byte_4_events_total * 10  # noqa
            ]
            remaining = remaining[2 + self.byte_4_events_total * 10 :]  # noqa
        else:
            self.byte_4_events = ""
            remaining = remaining[2:]

        self.byte_8_events_total = int(remaining[0:2], 16)
        if self.byte_8_events_total > 1:
            self.byte_8_events = remaining[2 : self.byte_8_events_total * 18]  # noqa

        else:
            self.byte_8_events = ""

    def load_events(self):
        for i in range(0, self.byte_1_events_total):
            event = self.byte_1_events[i * 4 : i * 4 + 4]  # noqa
            key = event[:2]
            verbose_name = self.verbose_names.get(key)
            if verbose_name:
                self.telemetry["values"][verbose_name] = int(event[2:], 16)

        for i in range(0, self.byte_2_events_total):
            event = self.byte_2_events[i * 6 : i * 6 + 6]  # noqa
            key = event[:2]
            verbose_name = self.verbose_names.get(key)
            if verbose_name:
                self.telemetry["values"][verbose_name] = int(event[2:], 16)

        for i in range(0, self.byte_4_events_total):
            event = self.byte_4_events[i * 10 : i * 10 + 10]  # noqa
            key = event[:2]
            verbose_name = self.verbose_names.get(key)
            if verbose_name:
                self.telemetry["values"][verbose_name] = int(event[2:], 16)

        for i in range(0, self.byte_8_events_total):
            event = self.byte_4_events[i * 18 : i * 18 + 18]  # noqa
            key = event[:2]
            verbose_name = self.verbose_names.get(key)
            if verbose_name:
                self.telemetry["values"][verbose_name] = int(event[2:], 16)

    def form_telemetry(self):
        self.load_events()
        return self.telemetry
