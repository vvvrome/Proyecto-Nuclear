from dataclasses import dataclass


@dataclass(frozen=True)
class TelemetryReading:
    timestamp_s: float
    variable: str
    value: float
    unit: str