class AVL:

    verbose_names = {
        "ef": "ignition",
        "f0": "movement",
        "15": "gsmSignal",
        "c8": "sleepMode",
        "45": "gnssStatus",
        "01": "digitalInput1",
        "02": "digitalInput2",
    }

    def __init__(self, data):
        self.data = data
        self.mapped_basic_data = {
            "timestamp": data[0:16],
            "priority": data[16:18],
            "longitude": data[18:26],
            "latitude": data[26:34],
            "altitude": data[34:38],
            "angle": data[38:42],
            "satellites": data[42:44],
            "speed": data[44:48],
            "event_io_id": data[48:50],
            "total_events": data[50:52],
        }
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

    def register_events(self, items):
        all_events = (
            items["byte_1_events"]
            + items["byte_2_events"]
            + items["byte_4_events"]
            + items["byte_8_events"]
        )
        for event in all_events:
            self.registered_events[event] = self.verbose_names[event]

    def parse_basic_items(self, items):
        # for item in self.telemetry['values']:

        for item in items["base"]:
            self.telemetry["values"][item] = int(self.mapped_basic_data[item], 16)

    def load_events(self, items):
        if items["byte_1_events"]:
            for i in range(0, self.byte_1_events_total):
                event = self.byte_1_events[i * 4 : i * 4 + 4]  # noqa
                key = event[:2]
                verbose_name = self.verbose_names.get(key)
                if verbose_name:
                    # if self.registered_events.get(key):
                    #     verbose_name = self.verbose_names.get(key)
                    self.telemetry["values"][verbose_name] = int(event[2:], 16)

        if items["byte_2_events"]:
            for i in range(0, self.byte_2_events_total):
                event = self.byte_2_events[i * 6 : i * 6 + 6]  # noqa
                key = event[:2]
                if self.registered_events.get(key):
                    verbose_name = self.verbose_names.get(key)
                    self.telemetry["values"][verbose_name] = int(event[2:], 16)

        if items["byte_4_events"]:
            for i in range(0, self.byte_4_events_total):
                event = self.byte_4_events[i * 10 : i * 10 + 10]  # noqa
                key = event[:2]
                if self.registered_events.get(key):
                    verbose_name = self.verbose_names.get(key)
                    self.telemetry["values"][verbose_name] = int(event[2:], 16)

        if items["byte_8_events"]:
            for i in range(0, self.byte_8_events_total):
                key = event[:2]
                if self.registered_events.get(key):
                    verbose_name = self.verbose_names.get(key)
                    self.telemetry["values"][verbose_name] = int(event[2:], 16)

    def form_telemetry(self, items: dict):
        # self.parse_basic_items(items)
        self.register_events(items)
        self.load_events(items)
        return self.telemetry
