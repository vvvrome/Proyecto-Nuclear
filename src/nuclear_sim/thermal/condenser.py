from dataclasses import dataclass
import math


@dataclass(frozen=True)
class CondenserState:
    """Estado instantáneo del condensador."""

    steam_power_mw: float
    mechanical_power_mw: float
    rejected_heat_mw: float
    condensed_heat_mw: float
    inlet_temperature_k: float
    outlet_temperature_k: float
    efficiency: float


class Condenser:
    """Modelo simplificado de condensador del ciclo térmico."""

    def __init__(
        self,
        efficiency: float = 0.95,
        reference_temperature_k: float = 313.15,
    ) -> None:
        if (
            not math.isfinite(efficiency)
            or not 0.0 < efficiency <= 1.0
        ):
            raise ValueError(
                "La eficiencia debe estar entre 0 y 1."
            )

        if (
            not math.isfinite(reference_temperature_k)
            or reference_temperature_k <= 0
        ):
            raise ValueError(
                "La temperatura de referencia debe ser "
                "positiva y finita."
            )

        self.efficiency = float(efficiency)
        self.reference_temperature_k = float(
            reference_temperature_k
        )

    def condense(
        self,
        steam_power_mw: float,
        mechanical_power_mw: float,
        inlet_temperature_k: float,
    ) -> CondenserState:
        """Condensa el vapor y calcula el calor rechazado."""

        values = (
            steam_power_mw,
            mechanical_power_mw,
            inlet_temperature_k,
        )

        if any(
            not math.isfinite(value)
            for value in values
        ):
            raise ValueError(
                "Todos los parámetros deben ser finitos."
            )

        if steam_power_mw < 0:
            raise ValueError(
                "La potencia del vapor no puede ser negativa."
            )

        if mechanical_power_mw < 0:
            raise ValueError(
                "La potencia mecánica no puede ser negativa."
            )

        if mechanical_power_mw > steam_power_mw:
            raise ValueError(
                "La potencia mecánica no puede superar "
                "la potencia del vapor."
            )

        if inlet_temperature_k <= 0:
            raise ValueError(
                "La temperatura de entrada debe ser positiva."
            )

        rejected_heat_mw = (
            steam_power_mw
            - mechanical_power_mw
        )

        condensed_heat_mw = (
            rejected_heat_mw
            * self.efficiency
        )

        temperature_excess = max(
            inlet_temperature_k
            - self.reference_temperature_k,
            0.0,
        )

        outlet_temperature_k = (
            self.reference_temperature_k
            + temperature_excess
            * (1.0 - self.efficiency)
        )

        return CondenserState(
            steam_power_mw=steam_power_mw,
            mechanical_power_mw=mechanical_power_mw,
            rejected_heat_mw=rejected_heat_mw,
            condensed_heat_mw=condensed_heat_mw,
            inlet_temperature_k=inlet_temperature_k,
            outlet_temperature_k=outlet_temperature_k,
            efficiency=self.efficiency,
        )