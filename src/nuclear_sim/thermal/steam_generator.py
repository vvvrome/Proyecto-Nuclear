from dataclasses import dataclass
import math


@dataclass(frozen=True)
class SteamState:
    """Estado del vapor generado."""

    thermal_power_mw: float
    steam_power_mw: float
    efficiency: float
    steam_temperature_k: float


class SteamGenerator:
    """Modelo simplificado de un generador de vapor."""

    def __init__(
        self,
        efficiency: float = 0.90,
        reference_temperature_k: float = 573.15,
    ) -> None:
        if not math.isfinite(efficiency) or not 0.0 < efficiency <= 1.0:
            raise ValueError(
                "La eficiencia debe estar entre 0 y 1."
            )

        if (
            not math.isfinite(reference_temperature_k)
            or reference_temperature_k <= 0
        ):
            raise ValueError(
                "La temperatura de referencia debe ser positiva y finita."
            )

        self.efficiency = float(efficiency)
        self.reference_temperature_k = float(reference_temperature_k)

    def generate(
        self,
        thermal_power_mw: float,
        primary_temperature_k: float,
    ) -> SteamState:
        """Genera vapor a partir de potencia térmica."""

        if not math.isfinite(thermal_power_mw) or thermal_power_mw < 0:
            raise ValueError(
                "La potencia térmica debe ser finita y no negativa."
            )

        if (
            not math.isfinite(primary_temperature_k)
            or primary_temperature_k <= 0
        ):
            raise ValueError(
                "La temperatura primaria debe ser positiva y finita."
            )

        steam_power = thermal_power_mw * self.efficiency

        temperature_difference = (
            primary_temperature_k - self.reference_temperature_k
        )

        steam_temperature = (
            self.reference_temperature_k
            + max(temperature_difference, 0.0) * 0.75
        )

        return SteamState(
            thermal_power_mw=thermal_power_mw,
            steam_power_mw=steam_power,
            efficiency=self.efficiency,
            steam_temperature_k=steam_temperature,
        )