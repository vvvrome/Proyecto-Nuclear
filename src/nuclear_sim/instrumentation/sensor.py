from dataclasses import dataclass
import math


@dataclass(frozen=True)
class SensorReading:
    """Lectura de un sensor."""

    name: str
    value: float
    unit: str
    timestamp_s: float
    status: str


class Sensor:
    """Sensor genérico de la planta."""

    def __init__(
        self,
        name: str,
        unit: str,
        initial_value: float = 0.0,
    ) -> None:
        if not name:
            raise ValueError("El nombre del sensor no puede estar vacío.")

        if not unit:
            raise ValueError("La unidad del sensor no puede estar vacía.")

        if not math.isfinite(initial_value):
            raise ValueError("El valor inicial debe ser finito.")

        self.name = name
        self.unit = unit
        self._value = float(initial_value)
        self._timestamp_s = 0.0
        self._status = "normal"

    def update(
        self,
        value: float,
        timestamp_s: float,
    ) -> SensorReading:
        """Actualiza el valor del sensor."""

        if not math.isfinite(value):
            raise ValueError("El valor del sensor debe ser finito.")

        if not math.isfinite(timestamp_s) or timestamp_s < 0:
            raise ValueError(
                "El timestamp debe ser finito y no negativo."
            )

        self._value = float(value)
        self._timestamp_s = float(timestamp_s)

        return self.read()

    def set_status(self, status: str) -> None:
        """Establece el estado del sensor."""

        if not status:
            raise ValueError("El estado no puede estar vacío.")

        self._status = status

    def read(self) -> SensorReading:
        """Devuelve la lectura actual."""

        return SensorReading(
            name=self.name,
            value=self._value,
            unit=self.unit,
            timestamp_s=self._timestamp_s,
            status=self._status,
        )