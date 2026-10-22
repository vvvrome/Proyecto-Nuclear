from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ThermalLossState:
    """Estado de las pérdidas térmicas."""

    input_power_mw: float
    lost_power_mw: float
    useful_power_mw: float
    loss_fraction: float


class ThermalLossModel:
    """Modelo simplificado de pérdidas térmicas del circuito."""

    def __init__(
        self,
        loss_fraction: float = 0.02,
    ) -> None:
        if (
            not math.isfinite(loss_fraction)
            or not 0.0 <= loss_fraction < 1.0
        ):
            raise ValueError(
                "La fracción de pérdidas debe estar entre 0 y 1."
            )

        self.loss_fraction = float(loss_fraction)

    def calculate(
        self,
        input_power_mw: float,
    ) -> ThermalLossState:
        """Calcula la potencia perdida y la potencia útil."""

        if (
            not math.isfinite(input_power_mw)
            or input_power_mw < 0.0
        ):
            raise ValueError(
                "La potencia de entrada debe ser finita y no negativa."
            )

        lost_power_mw = (
            input_power_mw * self.loss_fraction
        )

        useful_power_mw = (
            input_power_mw - lost_power_mw
        )

        return ThermalLossState(
            input_power_mw=input_power_mw,
            lost_power_mw=lost_power_mw,
            useful_power_mw=useful_power_mw,
            loss_fraction=self.loss_fraction,
        )