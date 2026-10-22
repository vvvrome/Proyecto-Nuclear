from dataclasses import dataclass
import math

from nuclear_sim.nuclear.kinetics.point_kinetics import PointKinetics


@dataclass(frozen=True)
class ReactorKineticsState:
    """Estado cinético del reactor."""

    time_s: float
    neutron_population: float
    precursor_population: float
    power_fraction: float
    power_mw: float


class ReactorKinetics:
    """Modelo dinámico de potencia basado en cinética puntual."""

    def __init__(
        self,
        rated_power_mw: float,
        initial_power_fraction: float = 1.0,
        point_kinetics: PointKinetics | None = None,
    ) -> None:
        if (
            not math.isfinite(rated_power_mw)
            or rated_power_mw <= 0
        ):
            raise ValueError(
                "La potencia nominal debe ser positiva y finita."
            )

        if (
            not math.isfinite(initial_power_fraction)
            or not 0.0 < initial_power_fraction <= 1.0
        ):
            raise ValueError(
                "La fracción de potencia inicial debe estar entre 0 y 1."
            )

        self.rated_power_mw = float(rated_power_mw)

        self.point_kinetics = (
            point_kinetics
            if point_kinetics is not None
            else PointKinetics()
        )

        self._time_s = 0.0
        self._reactivity = 0.0

        # La población neutrónica inicial se normaliza respecto
        # a la potencia inicial del reactor.
        self._neutron_population = float(
            initial_power_fraction
        )

        # En estado crítico, los precursores deben encontrarse
        # en equilibrio con la población neutrónica.
        self._precursor_population = (
            self.point_kinetics.equilibrium_precursor_population(
                self._neutron_population
            )
        )

        self._power_fraction = float(
            initial_power_fraction
        )

    @property
    def power_mw(self) -> float:
        """Potencia instantánea del reactor."""

        return self.rated_power_mw * self._power_fraction

    @property
    def neutron_population(self) -> float:
        """Población neutrónica relativa."""

        return self._neutron_population

    @property
    def precursor_population(self) -> float:
        """Población relativa de precursores."""

        return self._precursor_population

    @property
    def time_s(self) -> float:
        """Tiempo de simulación."""

        return self._time_s

    @property
    def reactivity(self) -> float:
        """Reactividad actual."""

        return self._reactivity

    def set_reactivity(self, reactivity: float) -> None:
        """Establece la reactividad del reactor."""

        if not math.isfinite(reactivity):
            raise ValueError(
                "La reactividad debe ser finita."
            )

        self._reactivity = float(reactivity)

    def state(self) -> ReactorKineticsState:
        """Devuelve el estado actual del reactor."""

        return ReactorKineticsState(
            time_s=self._time_s,
            neutron_population=self._neutron_population,
            precursor_population=self._precursor_population,
            power_fraction=self._power_fraction,
            power_mw=self.power_mw,
        )

    def advance(
        self,
        dt_s: float,
        reactivity: float | None = None,
    ) -> ReactorKineticsState:
        """Avanza la cinética del reactor."""

        if not math.isfinite(dt_s) or dt_s < 0:
            raise ValueError(
                "El intervalo de tiempo debe ser finito y no negativo."
            )

        if reactivity is not None:
            if not math.isfinite(reactivity):
                raise ValueError(
                    "La reactividad debe ser finita."
                )

            self._reactivity = float(reactivity)

        if dt_s == 0.0:
            return self.state()

        kinetic_state = self.point_kinetics.step(
            neutron_population=self._neutron_population,
            precursor_population=self._precursor_population,
            reactivity=self._reactivity,
            dt_s=dt_s,
        )

        self._neutron_population = (
            kinetic_state.neutron_population
        )

        self._precursor_population = (
            kinetic_state.precursor_population
        )

        self._time_s += dt_s

        # La potencia está directamente relacionada con
        # la población neutrónica.
        self._power_fraction = max(
            self._neutron_population,
            0.0,
        )

        return self.state()

    def scram(self) -> None:
        """Realiza un apagado rápido del reactor."""

        self._power_fraction = 0.0
        self._neutron_population = 0.0

        self._reactivity = 0.0

    def reset(self) -> ReactorKineticsState:
        """Restablece el reactor a su estado crítico inicial."""

        self._time_s = 0.0
        self._reactivity = 0.0

        self._neutron_population = self._power_fraction = (
            self._power_fraction
            if self._power_fraction > 0.0
            else 1.0
        )

        self._precursor_population = (
            self.point_kinetics.equilibrium_precursor_population(
                self._neutron_population
            )
        )

        return self.state()