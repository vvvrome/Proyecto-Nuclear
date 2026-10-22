from dataclasses import dataclass
import math


@dataclass(frozen=True)
class EnergyBalanceState:
    """Balance energético completo de la planta."""

    input_power_mw: float

    thermal_losses_mw: float
    useful_thermal_power_mw: float

    steam_power_mw: float
    steam_generation_losses_mw: float

    mechanical_power_mw: float
    turbine_losses_mw: float

    electrical_power_mw: float
    generator_losses_mw: float

    rejected_heat_mw: float

    auxiliary_power_mw: float
    net_electrical_power_mw: float

    balance_error_mw: float

    thermal_efficiency: float
    net_efficiency: float


class EnergyBalance:
    """Calcula y valida el balance energético de la planta."""

    def calculate(
        self,
        input_power_mw: float,
        thermal_losses_mw: float,
        useful_thermal_power_mw: float,
        steam_power_mw: float,
        mechanical_power_mw: float,
        electrical_power_mw: float,
        rejected_heat_mw: float,
        auxiliary_power_mw: float,
    ) -> EnergyBalanceState:

        values = {
            "input_power_mw": input_power_mw,
            "thermal_losses_mw": thermal_losses_mw,
            "useful_thermal_power_mw": useful_thermal_power_mw,
            "steam_power_mw": steam_power_mw,
            "mechanical_power_mw": mechanical_power_mw,
            "electrical_power_mw": electrical_power_mw,
            "rejected_heat_mw": rejected_heat_mw,
            "auxiliary_power_mw": auxiliary_power_mw,
        }

        for name, value in values.items():
            if not math.isfinite(value):
                raise ValueError(
                    f"{name} debe ser finito."
                )

            if value < 0.0:
                raise ValueError(
                    f"{name} no puede ser negativo."
                )

        if useful_thermal_power_mw > (
            input_power_mw - thermal_losses_mw
        ) + 1e-9:
            raise ValueError(
                "La potencia térmica útil no puede superar "
                "la potencia disponible."
            )

        if steam_power_mw > useful_thermal_power_mw + 1e-9:
            raise ValueError(
                "La potencia de vapor no puede superar "
                "la potencia térmica útil."
            )

        if mechanical_power_mw > steam_power_mw + 1e-9:
            raise ValueError(
                "La potencia mecánica no puede superar "
                "la potencia de vapor."
            )

        if electrical_power_mw > mechanical_power_mw + 1e-9:
            raise ValueError(
                "La potencia eléctrica no puede superar "
                "la potencia mecánica."
            )

        if rejected_heat_mw > steam_power_mw + 1e-9:
            raise ValueError(
                "El calor rechazado no puede superar "
                "la potencia de vapor."
            )

        if auxiliary_power_mw > electrical_power_mw + 1e-9:
            raise ValueError(
                "La potencia auxiliar no puede superar "
                "la potencia eléctrica generada."
            )

        steam_generation_losses_mw = (
            useful_thermal_power_mw
            - steam_power_mw
        )

        turbine_losses_mw = (
            steam_power_mw
            - mechanical_power_mw
        )

        generator_losses_mw = (
            mechanical_power_mw
            - electrical_power_mw
        )

        net_electrical_power_mw = (
            electrical_power_mw
            - auxiliary_power_mw
        )

        accounted_power_mw = (
            thermal_losses_mw
            + steam_generation_losses_mw
            + rejected_heat_mw
            + generator_losses_mw
            + net_electrical_power_mw
            + auxiliary_power_mw
        )

        balance_error_mw = (
            input_power_mw
            - accounted_power_mw
        )

        thermal_efficiency = (
            electrical_power_mw / input_power_mw
            if input_power_mw > 0.0
            else 0.0
        )

        net_efficiency = (
            net_electrical_power_mw / input_power_mw
            if input_power_mw > 0.0
            else 0.0
        )

        return EnergyBalanceState(
            input_power_mw=input_power_mw,
            thermal_losses_mw=thermal_losses_mw,
            useful_thermal_power_mw=useful_thermal_power_mw,
            steam_power_mw=steam_power_mw,
            steam_generation_losses_mw=(
                steam_generation_losses_mw
            ),
            mechanical_power_mw=mechanical_power_mw,
            turbine_losses_mw=turbine_losses_mw,
            electrical_power_mw=electrical_power_mw,
            generator_losses_mw=generator_losses_mw,
            rejected_heat_mw=rejected_heat_mw,
            auxiliary_power_mw=auxiliary_power_mw,
            net_electrical_power_mw=(
                net_electrical_power_mw
            ),
            balance_error_mw=balance_error_mw,
            thermal_efficiency=thermal_efficiency,
            net_efficiency=net_efficiency,
        )