from dataclasses import dataclass
import math


@dataclass(frozen=True)
class HeatTransferState:
    """Estado de transferencia de calor."""

    reactor_power_mw: float
    transferred_power_mw: float
    efficiency: float


class HeatTransferModel:
    """Modelo simplificado de transferencia de calor."""

    def __init__(self, efficiency: float = 0.95) -> None:
        if not math.isfinite(efficiency) or not 0.0 < efficiency <= 1.0:
            raise ValueError(
                "La eficiencia debe estar entre 0 y 1."
            )

        self.efficiency = float(efficiency)

    def transfer(self, reactor_power_mw: float) -> HeatTransferState:
        """Calcula la potencia transferida al refrigerante."""

        if not math.isfinite(reactor_power_mw) or reactor_power_mw < 0:
            raise ValueError(
                "La potencia del reactor debe ser finita y no negativa."
            )

        transferred_power = reactor_power_mw * self.efficiency

        return HeatTransferState(
            reactor_power_mw=reactor_power_mw,
            transferred_power_mw=transferred_power,
            efficiency=self.efficiency,
        )