from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ReactorState:
    """Estado instantáneo simplificado del reactor."""

    time_s: float
    power_mw: float
    temperature_k: float
    neutron_flux: float
    status: str


class Reactor:
    """Modelo básico de potencia de un reactor nuclear."""

    def __init__(
        self,
        rated_power_mw: float,
        initial_temperature_k: float = 573.15,
    ) -> None:
        if not math.isfinite(rated_power_mw) or rated_power_mw <= 0:
            raise ValueError(
                "La potencia nominal debe ser positiva y finita."
            )

        if (
            not math.isfinite(initial_temperature_k)
            or initial_temperature_k <= 0
        ):
            raise ValueError(
                "La temperatura inicial debe ser positiva y finita."
            )

        self.rated_power_mw = float(rated_power_mw)
        self.initial_temperature_k = float(initial_temperature_k)

        self._power_fraction = 0.0
        self._time_s = 0.0

    @property
    def power_mw(self) -> float:
        return self.rated_power_mw * self._power_fraction

    def set_power_fraction(self, fraction: float) -> None:
        """Establece la potencia entre 0 y 100 %."""

        if not math.isfinite(fraction):
            raise ValueError("La fracción de potencia debe ser finita.")

        if not 0.0 <= fraction <= 1.0:
            raise ValueError(
                "La fracción de potencia debe estar entre 0 y 1."
            )

        self._power_fraction = float(fraction)

    def ramp_power(self, target_fraction: float, rate_per_s: float, dt_s: float) -> None:
        """Acerca progresivamente la potencia al objetivo."""

        if not math.isfinite(target_fraction) or not 0.0 <= target_fraction <= 1.0:
            raise ValueError(
                "La potencia objetivo debe estar entre 0 y 1."
            )

        if not math.isfinite(rate_per_s) or rate_per_s <= 0:
            raise ValueError(
                "La velocidad de cambio debe ser positiva y finita."
            )

        if not math.isfinite(dt_s) or dt_s < 0:
            raise ValueError(
                "El intervalo de tiempo debe ser finito y no negativo."
            )

        maximum_change = rate_per_s * dt_s
        difference = target_fraction - self._power_fraction

        if abs(difference) <= maximum_change:
            self._power_fraction = target_fraction
        else:
            self._power_fraction += math.copysign(
                maximum_change,
                difference,
            )

    def state(self) -> ReactorState:
        """Devuelve el estado actual del reactor."""

        power = self.power_mw

        temperature_rise = 200.0 * self._power_fraction
        temperature = self.initial_temperature_k + temperature_rise

        if power == 0.0:
            status = "shutdown"
        elif self._power_fraction < 0.05:
            status = "startup"
        elif self._power_fraction < 0.95:
            status = "operating"
        else:
            status = "full_power"

        return ReactorState(
            time_s=self._time_s,
            power_mw=power,
            temperature_k=temperature,
            neutron_flux=self._power_fraction,
            status=status,
        )

    def advance(self, dt_s: float) -> ReactorState:
        """Avanza el reloj del reactor sin modificar su potencia."""

        if not math.isfinite(dt_s) or dt_s < 0:
            raise ValueError(
                "El intervalo de tiempo debe ser finito y no negativo."
            )

        self._time_s += dt_s
        return self.state()
    
    def scram(self) -> None:
        """Realiza un apagado rápido de emergencia del reactor."""

        self._power_fraction = 0.0