from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ThermalBalance:
    """Balance energético sensible de un volumen de fluido."""

    mass_kg: float
    specific_heat_j_kg_k: float
    temperature_change_k: float
    energy_j: float


@dataclass(frozen=True)
class ConvectiveHeatTransfer:
    """Transferencia de calor por convección."""

    coefficient_w_m2_k: float
    area_m2: float
    temperature_difference_k: float
    heat_rate_w: float


def sensible_energy(
    mass_kg: float,
    specific_heat_j_kg_k: float,
    temperature_change_k: float,
) -> ThermalBalance:
    """Calcula Q = m c_p Delta T."""

    _positive(mass_kg, "La masa debe ser positiva y finita.")
    _positive(
        specific_heat_j_kg_k,
        "El calor específico debe ser positivo y finito.",
    )
    _finite(temperature_change_k, "El cambio de temperatura debe ser finito.")

    energy_j = mass_kg * specific_heat_j_kg_k * temperature_change_k

    return ThermalBalance(
        mass_kg=mass_kg,
        specific_heat_j_kg_k=specific_heat_j_kg_k,
        temperature_change_k=temperature_change_k,
        energy_j=energy_j,
    )


def temperature_change_from_energy(
    energy_j: float,
    mass_kg: float,
    specific_heat_j_kg_k: float,
) -> float:
    """Despeja Delta T = Q / (m c_p)."""

    _finite(energy_j, "La energía debe ser finita.")
    _positive(mass_kg, "La masa debe ser positiva y finita.")
    _positive(
        specific_heat_j_kg_k,
        "El calor específico debe ser positivo y finito.",
    )

    return energy_j / (mass_kg * specific_heat_j_kg_k)


def convective_heat_rate(
    coefficient_w_m2_k: float,
    area_m2: float,
    temperature_difference_k: float,
) -> ConvectiveHeatTransfer:
    """Calcula Q_dot = h A Delta T."""

    _positive(
        coefficient_w_m2_k,
        "El coeficiente convectivo debe ser positivo y finito.",
    )
    _positive(area_m2, "El área debe ser positiva y finita.")
    _finite(
        temperature_difference_k,
        "La diferencia de temperatura debe ser finita.",
    )

    heat_rate_w = (
        coefficient_w_m2_k
        * area_m2
        * temperature_difference_k
    )

    return ConvectiveHeatTransfer(
        coefficient_w_m2_k=coefficient_w_m2_k,
        area_m2=area_m2,
        temperature_difference_k=temperature_difference_k,
        heat_rate_w=heat_rate_w,
    )


def _finite(value: float, message: str) -> None:
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(message)


def _positive(value: float, message: str) -> None:
    _finite(value, message)
    if value <= 0:
        raise ValueError(message)
