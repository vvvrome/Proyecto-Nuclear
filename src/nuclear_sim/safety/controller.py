from nuclear_sim.plant.reactor import Reactor
from nuclear_sim.safety.system import SafetyAssessment


class SafetyController:
    """Controlador de respuesta ante condiciones de seguridad."""

    def __init__(self, reactor: Reactor) -> None:
        self.reactor = reactor

    def apply(self, assessment: SafetyAssessment) -> None:
        """Aplica la respuesta correspondiente al estado de seguridad."""

        if assessment.overall_status == "critical":
            self.reactor.scram()