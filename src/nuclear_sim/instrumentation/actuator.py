from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ActuatorState:
    """Estado de un actuador."""

    name: str
    position: float
    timestamp_s: float
    status: str


class Actuator:
    """Actuador genérico de la planta."""

    def __init__(
        self,
        name: str,
        initial_position: float = 0.0,
    ) -> None:
        if not name:
            raise ValueError("El nombre del actuador no puede estar vacío.")

        if (
            not math.isfinite(initial_position)
            or not 0.0 <= initial_position <= 1.0
        ):
            raise ValueError(
                "La posición inicial debe estar entre 0 y 1."
            )

        self.name = name
        self._position = float(initial_position)
        self._timestamp_s = 0.0
        self._status = "ready"

    def set_position(
        self,
        position: float,
        timestamp_s: float,
    ) -> ActuatorState:
        """Establece la posición del actuador."""

        if not math.isfinite(position) or not 0.0 <= position <= 1.0:
            raise ValueError(
                "La posición debe estar entre 0 y 1."
            )

        if not math.isfinite(timestamp_s) or timestamp_s < 0:
            raise ValueError(
                "El timestamp debe ser finito y no negativo."
            )

        self._position = float(position)
        self._timestamp_s = float(timestamp_s)

        return self.state()

    def set_status(self, status: str) -> None:
        """Establece el estado del actuador."""

        if not status:
            raise ValueError("El estado no puede estar vacío.")

        self._status = status

    def state(self) -> ActuatorState:
        """Devuelve el estado actual."""

        return ActuatorState(
            name=self.name,
            position=self._position,
            timestamp_s=self._timestamp_s,
            status=self._status,
        )