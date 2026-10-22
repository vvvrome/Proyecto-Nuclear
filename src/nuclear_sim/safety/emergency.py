from dataclasses import dataclass

from nuclear_sim.plant.reactor import Reactor


@dataclass(frozen=True)
class EmergencyState:
    """Estado del sistema de emergencia."""

    active: bool
    cooling_active: bool
    reactor_scrammed: bool


class EmergencySystem:
    """Gestiona las respuestas de emergencia de la planta."""

    def __init__(self, reactor: Reactor) -> None:
        self.reactor = reactor
        self._active = False
        self._cooling_active = False

    def activate(self) -> EmergencyState:
        """Activa el sistema de emergencia."""

        self._active = True
        self._cooling_active = True
        self.reactor.scram()

        return self.state()

    def deactivate(self) -> EmergencyState:
        """Desactiva el sistema de emergencia."""

        self._active = False
        self._cooling_active = False

        return self.state()

    def state(self) -> EmergencyState:
        """Devuelve el estado actual."""

        return EmergencyState(
            active=self._active,
            cooling_active=self._cooling_active,
            reactor_scrammed=self.reactor.state().power_mw == 0.0,
        )