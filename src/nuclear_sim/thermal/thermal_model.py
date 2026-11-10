from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ThermalState:
    """Estado térmico instantáneo del sistema."""

    temperature_k: float
    thermal_power_mw: float
    heat_removed_mw: float


class ThermalModel:
    """Modelo térmico simplificado del reactor."""

    def __init__(
        self,
        initial_temperature_k: float = 573.15,
        thermal_capacity_mj_per_k: float = 1000.0,
    ) -> None:
        if (
            not math.isfinite(initial_temperature_k)
            or initial_temperature_k <= 0
        ):
            raise ValueError(
                "La temperatura inicial debe ser positiva y finita."
            )

        if (
            not math.isfinite(thermal_capacity_mj_per_k)
            or thermal_capacity_mj_per_k <= 0
        ):
            raise ValueError(
                "La capacidad térmica debe ser positiva y finita."
            )

        self.initial_temperature_k = float(initial_temperature_k)
        self.temperature_k = self.initial_temperature_k
        self.thermal_capacity_mj_per_k = float(
            thermal_capacity_mj_per_k
        )

    def reset(self) -> None:
        """Restaura el estado térmico a sus condiciones iniciales."""

        self.temperature_k = self.initial_temperature_k

    def step(
        self,
        thermal_power_mw: float,
        heat_removed_mw: float,
        dt_s: float,
    ) -> ThermalState:
        """Avanza el estado térmico durante un intervalo."""

        if not math.isfinite(thermal_power_mw) or thermal_power_mw < 0:
            raise ValueError(
                "La potencia térmica debe ser finita y no negativa."
            )

        if not math.isfinite(heat_removed_mw) or heat_removed_mw < 0:
            raise ValueError(
                "El calor extraído debe ser finito y no negativo."
            )

        if not math.isfinite(dt_s) or dt_s < 0:
            raise ValueError(
                "El intervalo de tiempo debe ser finito y no negativo."
            )

        net_power_mw = thermal_power_mw - heat_removed_mw

        energy_mj = net_power_mw * dt_s

        temperature_change_k = (
            energy_mj / self.thermal_capacity_mj_per_k
        )

        self.temperature_k += temperature_change_k

        return ThermalState(
            temperature_k=self.temperature_k,
            thermal_power_mw=thermal_power_mw,
            heat_removed_mw=heat_removed_mw,
        )