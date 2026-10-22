from dataclasses import dataclass
import math


@dataclass(frozen=True)
class PumpState:
    """Estado instantáneo de la bomba."""

    mass_flow_kg_s: float
    inlet_pressure_mpa: float
    outlet_pressure_mpa: float
    inlet_temperature_k: float
    outlet_temperature_k: float
    pressure_difference_mpa: float
    hydraulic_power_mw: float
    electrical_power_mw: float
    efficiency: float


class Pump:
    """Modelo simplificado de una bomba de circulación."""

    def __init__(
        self,
        efficiency: float = 0.85,
        fluid_density_kg_m3: float = 1000.0,
    ) -> None:

        if (
            not math.isfinite(efficiency)
            or not 0.0 < efficiency <= 1.0
        ):
            raise ValueError(
                "La eficiencia debe estar entre 0 y 1."
            )

        if (
            not math.isfinite(fluid_density_kg_m3)
            or fluid_density_kg_m3 <= 0
        ):
            raise ValueError(
                "La densidad debe ser positiva y finita."
            )

        self.efficiency = float(efficiency)
        self.fluid_density_kg_m3 = float(
            fluid_density_kg_m3
        )

    def pump(
        self,
        mass_flow_kg_s: float,
        inlet_pressure_mpa: float,
        outlet_pressure_mpa: float,
        inlet_temperature_k: float,
    ) -> PumpState:
        """Calcula el consumo de potencia de la bomba."""

        values = (
            mass_flow_kg_s,
            inlet_pressure_mpa,
            outlet_pressure_mpa,
            inlet_temperature_k,
        )

        if not all(math.isfinite(value) for value in values):
            raise ValueError(
                "Los parámetros deben ser finitos."
            )

        if mass_flow_kg_s <= 0:
            raise ValueError(
                "El caudal másico debe ser positivo."
            )

        if inlet_pressure_mpa <= 0:
            raise ValueError(
                "La presión de entrada debe ser positiva."
            )

        if outlet_pressure_mpa <= 0:
            raise ValueError(
                "La presión de salida debe ser positiva."
            )

        if outlet_pressure_mpa < inlet_pressure_mpa:
            raise ValueError(
                "La presión de salida no puede ser menor "
                "que la presión de entrada."
            )

        if inlet_temperature_k <= 0:
            raise ValueError(
                "La temperatura debe ser positiva."
            )

        pressure_difference_mpa = (
            outlet_pressure_mpa
            - inlet_pressure_mpa
        )

        # ΔP en MPa -> Pa
        pressure_difference_pa = (
            pressure_difference_mpa * 1_000_000.0
        )

        # P_hid = caudal volumétrico × ΔP
        volumetric_flow_m3_s = (
            mass_flow_kg_s
            / self.fluid_density_kg_m3
        )

        hydraulic_power_w = (
            volumetric_flow_m3_s
            * pressure_difference_pa
        )

        hydraulic_power_mw = (
            hydraulic_power_w / 1_000_000.0
        )

        electrical_power_mw = (
            hydraulic_power_mw
            / self.efficiency
        )

        # Modelo simplificado:
        # no se introduce todavía calentamiento por compresión.
        outlet_temperature_k = inlet_temperature_k

        return PumpState(
            mass_flow_kg_s=mass_flow_kg_s,
            inlet_pressure_mpa=inlet_pressure_mpa,
            outlet_pressure_mpa=outlet_pressure_mpa,
            inlet_temperature_k=inlet_temperature_k,
            outlet_temperature_k=outlet_temperature_k,
            pressure_difference_mpa=pressure_difference_mpa,
            hydraulic_power_mw=hydraulic_power_mw,
            electrical_power_mw=electrical_power_mw,
            efficiency=self.efficiency,
        )