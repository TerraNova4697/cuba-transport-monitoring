from dataclasses import dataclass
from datetime import datetime


@dataclass
class Device:
    name: str
    id: str
    telemetry: list | None = None
    idling: int | None = None
    no_idling: int | None = None
    date: datetime | None = None
