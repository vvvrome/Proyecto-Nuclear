from nuclear_sim.instrumentation.actuator import Actuator
from nuclear_sim.instrumentation.sensor import Sensor


class InstrumentationSystem:
    """Gestiona sensores y actuadores de la planta."""

    def __init__(self) -> None:
        self._sensors: dict[str, Sensor] = {}
        self._actuators: dict[str, Actuator] = {}

    def add_sensor(self, sensor: Sensor) -> None:
        """Registra un sensor."""

        if sensor.name in self._sensors:
            raise ValueError(
                f"Ya existe un sensor llamado '{sensor.name}'."
            )

        self._sensors[sensor.name] = sensor

    def add_actuator(self, actuator: Actuator) -> None:
        """Registra un actuador."""

        if actuator.name in self._actuators:
            raise ValueError(
                f"Ya existe un actuador llamado '{actuator.name}'."
            )

        self._actuators[actuator.name] = actuator

    def get_sensor(self, name: str) -> Sensor:
        """Obtiene un sensor por su nombre."""

        try:
            return self._sensors[name]
        except KeyError as exc:
            raise KeyError(
                f"No existe el sensor '{name}'."
            ) from exc

    def get_actuator(self, name: str) -> Actuator:
        """Obtiene un actuador por su nombre."""

        try:
            return self._actuators[name]
        except KeyError as exc:
            raise KeyError(
                f"No existe el actuador '{name}'."
            ) from exc

    def sensor_count(self) -> int:
        """Devuelve el número de sensores registrados."""

        return len(self._sensors)

    def actuator_count(self) -> int:
        """Devuelve el número de actuadores registrados."""

        return len(self._actuators)