from dataclasses import dataclass
import math


@dataclass(frozen=True)
class TurbineState:
    """Estado de la turbina."""

    steam_power_mw: float
    mechanical_power_mw: float
    efficiency: float
    rotational_speed_rpm: float


class Turbine:
    """Modelo simplificado de una turbina de vapor."""

    def __init__(
        self,
        efficiency: float = 0.85,
        rated_speed_rpm: float = 3000.0,
    ) -> None:
        if not math.isfinite(efficiency) or not 0.0 < efficiency <= 1.0:
            raise ValueError(
                "La eficiencia debe estar entre 0 y 1."
            )

        if not math.isfinite(rated_speed_rpm) or rated_speed_rpm <= 0:
            raise ValueError(
                "La velocidad nominal debe ser positiva y finita."
            )

        self.efficiency = float(efficiency)
        self.rated_speed_rpm = float(rated_speed_rpm)

    def expand(self, steam_power_mw: float) -> TurbineState:
        """Convierte potencia del vapor en potencia mecánica."""

        if not math.isfinite(steam_power_mw) or steam_power_mw < 0:
            raise ValueError(
                "La potencia del vapor debe ser finita y no negativa."
            )

        mechanical_power = steam_power_mw * self.efficiency

        speed = (
            0.0
            if steam_power_mw == 0.0
            else self.rated_speed_rpm
        )

        return TurbineState(
            steam_power_mw=steam_power_mw,
            mechanical_power_mw=mechanical_power,
            efficiency=self.efficiency,
            rotational_speed_rpm=speed,
        )