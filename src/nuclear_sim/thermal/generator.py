from dataclasses import dataclass
import math


@dataclass(frozen=True)
class GeneratorState:
    """Estado del generador eléctrico."""

    mechanical_power_mw: float
    electrical_power_mw: float
    efficiency: float
    frequency_hz: float


class Generator:
    """Modelo simplificado de un generador eléctrico."""

    def __init__(
        self,
        efficiency: float = 0.98,
        frequency_hz: float = 50.0,
    ) -> None:
        if not math.isfinite(efficiency) or not 0.0 < efficiency <= 1.0:
            raise ValueError(
                "La eficiencia debe estar entre 0 y 1."
            )

        if not math.isfinite(frequency_hz) or frequency_hz <= 0:
            raise ValueError(
                "La frecuencia debe ser positiva y finita."
            )

        self.efficiency = float(efficiency)
        self.frequency_hz = float(frequency_hz)

    def generate(self, mechanical_power_mw: float) -> GeneratorState:
        """Convierte potencia mecánica en potencia eléctrica."""

        if not math.isfinite(mechanical_power_mw) or mechanical_power_mw < 0:
            raise ValueError(
                "La potencia mecánica debe ser finita y no negativa."
            )

        electrical_power = mechanical_power_mw * self.efficiency

        return GeneratorState(
            mechanical_power_mw=mechanical_power_mw,
            electrical_power_mw=electrical_power,
            efficiency=self.efficiency,
            frequency_hz=self.frequency_hz,
        )