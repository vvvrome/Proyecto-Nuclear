from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ShieldingState:
    """Atenuación exponencial de una radiación monoenergética idealizada."""

    initial_intensity: float
    thickness_m: float
    linear_attenuation_coefficient_m_inv: float
    transmitted_intensity: float
    transmission_factor: float


class ShieldingModel:
    """Modelo I(x)=I0 exp(-mu x), sin buildup."""

    def __init__(self, linear_attenuation_coefficient_m_inv: float) -> None:
        if (
            not math.isfinite(linear_attenuation_coefficient_m_inv)
            or linear_attenuation_coefficient_m_inv < 0
        ):
            raise ValueError("El coeficiente de atenuación debe ser válido.")

        self.mu = float(linear_attenuation_coefficient_m_inv)

    def calculate(self, initial_intensity: float, thickness_m: float) -> ShieldingState:
        if not math.isfinite(initial_intensity) or initial_intensity < 0:
            raise ValueError("La intensidad inicial debe ser válida.")

        if not math.isfinite(thickness_m) or thickness_m < 0:
            raise ValueError("El espesor debe ser finito y no negativo.")

        transmission = math.exp(-self.mu * thickness_m)

        return ShieldingState(
            initial_intensity=initial_intensity,
            thickness_m=thickness_m,
            linear_attenuation_coefficient_m_inv=self.mu,
            transmitted_intensity=initial_intensity * transmission,
            transmission_factor=transmission,
        )
