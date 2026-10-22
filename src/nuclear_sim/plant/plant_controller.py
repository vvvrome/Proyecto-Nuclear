from typing import TYPE_CHECKING

from nuclear_sim.plant.reactor import Reactor
from nuclear_sim.instrumentation.actuator import Actuator

if TYPE_CHECKING:
    from nuclear_sim.plant.plant_instrumentation import PlantInstrumentation
    from nuclear_sim.plant.reactor_dynamics import ReactorDynamics


class PlantController:
    """Controlador de los actuadores principales de la planta."""

    def __init__(
        self,
        reactor: Reactor,
        instrumentation: "PlantInstrumentation | None" = None,
        reactor_dynamics: "ReactorDynamics | None" = None,
        control_gain: float = 0.006,
        control_reactivity_limit: float = 0.002,
    ) -> None:
        self.reactor = reactor
        self.reactor_dynamics = reactor_dynamics
        if control_gain <= 0:
            raise ValueError(
                "La ganancia de control debe de ser positiva"
            )
        if control_reactivity_limit <= 0:
            raise ValueError(
                "El limite de reactividad debe de ser positivo"
            )

        self.control_gain = float(control_gain)
        self.control_reactivity_limit = float(
            control_reactivity_limit
        )
        self.target_power_fraction = (
            reactor.state().power_mw
            / reactor.rated_power_mw
        )

        if instrumentation is not None:
            self.power_control = instrumentation.system.get_actuator(
                "reactor_power_control"
            )
            self.scram_actuator = instrumentation.system.get_actuator(
                "scram"
            )
        else:
            self.power_control = Actuator(
                name="reactor_power_control",
                initial_position=(
                    reactor.state().power_mw
                    / reactor.rated_power_mw
                ),
            )

            self.scram_actuator = Actuator(
                name="scram",
                initial_position=0.0,
            )

    def update_control(self) -> float:
        """Actualiza la reactividad de control segun el error de potencia"""

        if self.reactor_dynamics is None:
            return 0.0

        current_state = self.reactor_dynamics.state()

        current_power_fraction = (
            current_state.power_mw
            / self.reactor.rated_power_mw
        )

        error = (
            self.target_power_fraction
            - current_power_fraction
        )

        control_reactivity = self.control_gain * error

        control_reactivity = max(
            -self.control_reactivity_limit,
            min(
                control_reactivity,
                self.control_reactivity_limit,
            ),
        )

        self.reactor_dynamics.set_control_reactivity(
            control_reactivity
        )

        return control_reactivity

    def set_reactor_power(
        self,
        power_fraction: float,
        timestamp_s: float,
    ):
        """Establece la potencia objetivo del reactor."""

        state = self.power_control.set_position(
            position=power_fraction,
            timestamp_s=timestamp_s,
        )

        self.target_power_fraction = power_fraction

        if self.reactor_dynamics is None:
            self.reactor.set_power_fraction(power_fraction)
        else:
            self.update_control()

        return state

    def scram(self, timestamp_s: float):
        """Activa el SCRAM del reactor."""

        state = self.scram_actuator.set_position(
            position=1.0,
            timestamp_s=timestamp_s,
        )

        self.reactor.scram()

        if self.reactor_dynamics is not None:
            self.reactor_dynamics.scram()

        return state

    def reset_scram(self, timestamp_s: float):
        """Restablece la posición del actuador SCRAM."""

        return self.scram_actuator.set_position(
            position=0.0,
            timestamp_s=timestamp_s,
        )

    def actuator_states(self):
        """Devuelve el estado actual de los actuadores."""

        return {
            "reactor_power_control": self.power_control.state(),
            "scram": self.scram_actuator.state(),
        }