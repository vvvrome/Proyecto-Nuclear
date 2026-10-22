from dataclasses import dataclass
import math


@dataclass(frozen=True)
class RadiationFieldState:
    """Campo idealizado de una fuente puntual isotrópica."""

    source_activity_bq: float
    emission_probability: float
    distance_m: float
    initial_rate: float
    attenuated_rate: float


class RadiationField:
    """Modelo geométrico 1/r² combinado con atenuación exp(-mu x)."""

    def __init__(self, attenuation_coefficient_m_inv: float = 0.0) -> None:
        if (
            not math.isfinite(attenuation_coefficient_m_inv)
            or attenuation_coefficient_m_inv < 0
        ):
            raise ValueError("El coeficiente de atenuación debe ser válido.")

        self.mu = float(attenuation_coefficient_m_inv)

    def calculate(
        self,
        source_activity_bq: float,
        emission_probability: float,
        distance_m: float,
        reference_rate: float = 1.0,
    ) -> RadiationFieldState:
        """Calcula una tasa proporcional a A p /(4 pi r²), con blindaje."""

        if not math.isfinite(source_activity_bq) or source_activity_bq < 0:
            raise ValueError("La actividad debe ser válida.")

        if (
            not math.isfinite(emission_probability)
            or not 0 <= emission_probability <= 1
        ):
            raise ValueError("La probabilidad de emisión debe estar entre 0 y 1.")

        if not math.isfinite(distance_m) or distance_m <= 0:
            raise ValueError("La distancia debe ser positiva y finita.")

        if not math.isfinite(reference_rate) or reference_rate < 0:
            raise ValueError("La tasa de referencia debe ser válida.")

        initial_rate = (
            reference_rate
            * source_activity_bq
            * emission_probability
            / (4.0 * math.pi * distance_m**2)
        )

        attenuated_rate = initial_rate * math.exp(-self.mu * distance_m)

        return RadiationFieldState(
            source_activity_bq=source_activity_bq,
            emission_probability=emission_probability,
            distance_m=distance_m,
            initial_rate=initial_rate,
            attenuated_rate=attenuated_rate,
        )
