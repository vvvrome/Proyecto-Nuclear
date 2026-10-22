from dataclasses import dataclass
import math


@dataclass(frozen=True)
class CoolantState:
    """Estado instantáneo del refrigerante."""

    mass_flow_kg_s: float
    inlet_temperature_k: float
    outlet_temperature_k: float
    pressure_mpa: float


class Coolant:
    """Modelo simplificado del circuito de refrigeración."""

    def __init__(
        self,
        mass_flow_kg_s: float,
        inlet_temperature_k: float,
        pressure_mpa: float,
        specific_heat_kj_kg_k: float = 4.18,
    ) -> None:
        if not math.isfinite(mass_flow_kg_s) or mass_flow_kg_s <= 0:
            raise ValueError(
                "El caudal másico debe ser positivo y finito."
            )

        if (
            not math.isfinite(inlet_temperature_k)
            or inlet_temperature_k <= 0
        ):
            raise ValueError(
                "La temperatura de entrada debe ser positiva y finita."
            )

        if not math.isfinite(pressure_mpa) or pressure_mpa <= 0:
            raise ValueError(
                "La presión debe ser positiva y finita."
            )

        if (
            not math.isfinite(specific_heat_kj_kg_k)
            or specific_heat_kj_kg_k <= 0
        ):
            raise ValueError(
                "El calor específico debe ser positivo y finito."
            )

        self.mass_flow_kg_s = float(mass_flow_kg_s)
        self.inlet_temperature_k = float(inlet_temperature_k)
        self.pressure_mpa = float(pressure_mpa)
        self.specific_heat_kj_kg_k = float(specific_heat_kj_kg_k)
        self._outlet_temperature_k = self.inlet_temperature_k

    def calculate_outlet_temperature(
        self,
        thermal_power_mw: float,
    ) -> float:
        """Calcula la temperatura de salida del refrigerante."""

        if not math.isfinite(thermal_power_mw) or thermal_power_mw < 0:
            raise ValueError(
                "La potencia térmica debe ser finita y no negativa."
            )

        # MW = MJ/s
        # cp = kJ/(kg K) = MJ/(1000 kg K)
        denominator = (
            self.mass_flow_kg_s
            * self.specific_heat_kj_kg_k
            / 1000.0
        )

        temperature_rise = thermal_power_mw / denominator

        self._outlet_temperature_k = (
            self.inlet_temperature_k + temperature_rise
        )

        return self._outlet_temperature_k

    def state(self) -> CoolantState:
        """Devuelve el estado actual."""

        return CoolantState(
            mass_flow_kg_s=self.mass_flow_kg_s,
            inlet_temperature_k=self.inlet_temperature_k,
            outlet_temperature_k=self._outlet_temperature_k,
            pressure_mpa=self.pressure_mpa,
        )