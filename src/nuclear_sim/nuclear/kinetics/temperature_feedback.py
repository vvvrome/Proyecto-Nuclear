from dataclasses import dataclass
import math


@dataclass(frozen=True)
class TemperatureFeedbackState:
    """Estado de la retroalimentación de reactividad por temperatura."""

    temperature_k: float
    reference_temperature_k: float
    temperature_reactivity: float
    external_reactivity: float
    total_reactivity: float


class TemperatureFeedback:
    """Modelo lineal de retroalimentación de reactividad por temperatura.

    La contribución térmica se calcula mediante:

        rho_T = alpha_T * (T - T_ref)

    y la reactividad total mediante:

        rho_total = rho_external + rho_T

    donde:

        T       = temperatura actual
        T_ref   = temperatura de referencia
        alpha_T = coeficiente de temperatura de reactividad
    """

    def __init__(
        self,
        reference_temperature_k: float = 573.15,
        temperature_coefficient_per_k: float = -1.0e-5,
    ) -> None:
        if (
            not math.isfinite(reference_temperature_k)
            or reference_temperature_k <= 0
        ):
            raise ValueError(
                "La temperatura de referencia debe ser positiva y finita."
            )

        if not math.isfinite(temperature_coefficient_per_k):
            raise ValueError(
                "El coeficiente de temperatura debe ser finito."
            )

        self.reference_temperature_k = float(
            reference_temperature_k
        )

        self.temperature_coefficient_per_k = float(
            temperature_coefficient_per_k
        )

    def calculate_temperature_reactivity(
        self,
        temperature_k: float,
    ) -> float:
        """Calcula la reactividad debida a la temperatura."""

        if not math.isfinite(temperature_k) or temperature_k <= 0:
            raise ValueError(
                "La temperatura debe ser positiva y finita."
            )

        temperature_difference = (
            temperature_k
            - self.reference_temperature_k
        )

        return (
            self.temperature_coefficient_per_k
            * temperature_difference
        )

    def calculate_total_reactivity(
        self,
        temperature_k: float,
        external_reactivity: float = 0.0,
    ) -> float:
        """Calcula la reactividad total."""

        if not math.isfinite(external_reactivity):
            raise ValueError(
                "La reactividad externa debe ser finita."
            )

        temperature_reactivity = (
            self.calculate_temperature_reactivity(
                temperature_k
            )
        )

        return (
            external_reactivity
            + temperature_reactivity
        )

    def state(
        self,
        temperature_k: float,
        external_reactivity: float = 0.0,
    ) -> TemperatureFeedbackState:
        """Devuelve el estado de retroalimentación."""

        temperature_reactivity = (
            self.calculate_temperature_reactivity(
                temperature_k
            )
        )

        total_reactivity = (
            external_reactivity
            + temperature_reactivity
        )

        return TemperatureFeedbackState(
            temperature_k=temperature_k,
            reference_temperature_k=self.reference_temperature_k,
            temperature_reactivity=temperature_reactivity,
            external_reactivity=external_reactivity,
            total_reactivity=total_reactivity,
        )