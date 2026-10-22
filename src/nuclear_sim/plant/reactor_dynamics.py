from dataclasses import dataclass
import math

from nuclear_sim.plant import reactivity
from nuclear_sim.plant.reactor_kinetics import ReactorKinetics
from nuclear_sim.nuclear.kinetics.temperature_feedback import (
    TemperatureFeedback,
)
from nuclear_sim.thermal.thermal_model import ThermalModel


@dataclass(frozen=True)
class ReactorDynamicsState:
    """Estado dinámico completo del reactor."""

    time_s: float
    neutron_population: float
    precursor_population: float
    power_fraction: float
    power_mw: float
    temperature_k: float
    external_reactivity: float
    temperature_reactivity: float
    total_reactivity: float


class ReactorDynamics:
    """Integra cinética neutrónica, temperatura y retroalimentación."""

    def __init__(
        self,
        rated_power_mw: float,
        initial_power_fraction: float = 1.0,
        thermal_model: ThermalModel | None = None,
        temperature_feedback: TemperatureFeedback | None = None,
        reactor_kinetics: ReactorKinetics | None = None,
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

        self.reactor_kinetics = (
            reactor_kinetics
            if reactor_kinetics is not None
            else ReactorKinetics(
                rated_power_mw=rated_power_mw,
                initial_power_fraction=initial_power_fraction,
            )
        )

        self.thermal_model = (
            thermal_model
            if thermal_model is not None
            else ThermalModel()
        )

        self.temperature_feedback = (
            temperature_feedback
            if temperature_feedback is not None
            else TemperatureFeedback(
                reference_temperature_k=self.thermal_model.temperature_k,
            )
        )

        self._external_reactivity = 0.0
        self._scrammed = False
        self._control_reactivity = 0.0
    @property
    def time_s(self) -> float:
        """Tiempo actual de simulación."""

        return self.reactor_kinetics.time_s

    @property
    def temperature_k(self) -> float:
        """Temperatura actual del reactor."""

        return self.thermal_model.temperature_k

    @property
    def external_reactivity(self) -> float:
        """Reactividad externa aplicada al reactor."""

        return self._external_reactivity

    def set_external_reactivity(
        self,
        reactivity: float,
    ) -> None:
        """Establece la reactividad externa."""

        if not math.isfinite(reactivity):
            raise ValueError(
                "La reactividad externa debe ser finita."
            )

        self._external_reactivity = float(reactivity)

    def state(self) -> ReactorDynamicsState:
        """Devuelve el estado dinámico actual."""

        temperature_reactivity = (
            self.temperature_feedback.calculate_temperature_reactivity(
                self.temperature_k
            )
        )

        total_reactivity = (
            self._external_reactivity
            + self._control_reactivity
            + temperature_reactivity
            
        )

        reactor_state = self.reactor_kinetics.state()

        return ReactorDynamicsState(
            time_s=self.time_s,
            neutron_population=(
                reactor_state.neutron_population
            ),
            precursor_population=(
                reactor_state.precursor_population
            ),
            power_fraction=(
                reactor_state.power_fraction
            ),
            power_mw=reactor_state.power_mw,
            temperature_k=self.temperature_k,
            external_reactivity=self._external_reactivity,
            temperature_reactivity=temperature_reactivity,
            total_reactivity=total_reactivity,
        )

    def step(
        self,
        dt_s: float,
        heat_removed_mw: float,
        external_reactivity: float | None = None,
    ) -> ReactorDynamicsState:
        """Avanza la dinámica acoplada del reactor."""
        if self._scrammed:
            return self.state()
        
        if not math.isfinite(dt_s) or dt_s < 0:
            raise ValueError(
                "El intervalo de tiempo debe ser finito y no negativo."
            )

        if (
            not math.isfinite(heat_removed_mw)
            or heat_removed_mw < 0
        ):
            raise ValueError(
                "El calor extraído debe ser finito y no negativo."
            )

        if external_reactivity is not None:
            if not math.isfinite(external_reactivity):
                raise ValueError(
                    "La reactividad externa debe ser finita."
                )

            self._external_reactivity = float(
                external_reactivity
            )

        if dt_s == 0.0:
            return self.state()

        temperature_reactivity = (
            self.temperature_feedback.calculate_temperature_reactivity(
                self.temperature_k
            )
        )

        total_reactivity = (
            self._external_reactivity
            + temperature_reactivity
            + self._control_reactivity
        )

        reactor_state = self.reactor_kinetics.advance(
            dt_s=dt_s,
            reactivity=total_reactivity,
        )

        thermal_state = self.thermal_model.step(
            thermal_power_mw=reactor_state.power_mw,
            heat_removed_mw=heat_removed_mw,
            dt_s=dt_s,
        )

        return ReactorDynamicsState(
            time_s=self.time_s,
            neutron_population=(
                reactor_state.neutron_population
            ),
            precursor_population=(
                reactor_state.precursor_population
            ),
            power_fraction=(
                reactor_state.power_fraction
            ),
            power_mw=reactor_state.power_mw,
            temperature_k=thermal_state.temperature_k,
            external_reactivity=self._external_reactivity,
            temperature_reactivity=(
                self.temperature_feedback
                .calculate_temperature_reactivity(
                    thermal_state.temperature_k
                )
            ),
            total_reactivity=(
                self._external_reactivity
                + self._control_reactivity
                + self.temperature_feedback
                .calculate_temperature_reactivity(
                    thermal_state.temperature_k
                )
            ),
        )

    def set_control_reactivity(self, reactivity: float) -> None:
        """Establece la reactividad aportada por el sistema de control."""

        if not math.isfinite(reactivity):
            raise ValueError(
                "La reactividad de control debe ser finita."
            )

        self._control_reactivity = float(reactivity)

    def control_reactivity(self) -> float:
        """Devuelve la reactividad de control actual."""

        return self._control_reactivity

    def scram(self) -> ReactorDynamicsState:
        """Realiza un apagado rápido del reactor."""
        self._scrammed = True

        self.reactor_kinetics.scram()

        return self.state()