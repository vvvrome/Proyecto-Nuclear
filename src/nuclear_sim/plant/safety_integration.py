from dataclasses import dataclass

from nuclear_sim.plant.reactor import Reactor
from nuclear_sim.safety.alarm import Alarm
from nuclear_sim.safety.controller import SafetyController
from nuclear_sim.safety.emergency import EmergencySystem
from nuclear_sim.safety.system import SafetyAssessment, SafetySystem


@dataclass(frozen=True)
class SafetyIntegrationState:
    """Estado combinado de seguridad de la planta."""

    assessment: SafetyAssessment
    alarms: tuple[Alarm, ...]
    emergency_active: bool


class SafetyIntegration:
    """Integra evaluación, alarmas y respuesta de emergencia."""

    def __init__(
        self,
        reactor: Reactor,
        safety_system: SafetySystem,
    ) -> None:
        self.reactor = reactor
        self.safety_system = safety_system
        self.controller = SafetyController(reactor)
        self.emergency_system = EmergencySystem(reactor)

    def evaluate(self, values: dict[str, float]) -> SafetyIntegrationState:
        """Evalúa la planta y aplica las respuestas de seguridad."""

        assessment = self.safety_system.evaluate(values)

        alarms: list[Alarm] = []

        for name, status in assessment.results.items():
            if status == "critical":
                alarms.append(
                    Alarm(
                        name=name,
                        severity="critical",
                        message=f"{name} ha superado el límite crítico.",
                    )
                )
            elif status == "warning":
                alarms.append(
                    Alarm(
                        name=name,
                        severity="warning",
                        message=f"{name} ha superado el límite de aviso.",
                    )
                )

        self.controller.apply(assessment)

        if assessment.overall_status == "critical":
            self.emergency_system.activate()

        return SafetyIntegrationState(
            assessment=assessment,
            alarms=tuple(alarms),
            emergency_active=self.emergency_system.state().active,
        )