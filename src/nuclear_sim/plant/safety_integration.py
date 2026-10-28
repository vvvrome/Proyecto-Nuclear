from dataclasses import dataclass

from nuclear_sim.plant.reactor import Reactor
from nuclear_sim.safety.alarm import Alarm
from nuclear_sim.safety.controller import SafetyController
from nuclear_sim.safety.emergency import EmergencySystem
from nuclear_sim.safety.incident import Incident
from nuclear_sim.safety.system import SafetyAssessment, SafetySystem


@dataclass(frozen=True)
class SafetyIntegrationState:
    """Estado combinado de seguridad de la planta."""

    assessment: SafetyAssessment
    alarms: tuple[Alarm, ...]
    incidents: tuple[Incident, ...]
    emergency_active: bool


class SafetyIntegration:
    """Integra evaluación, alarmas, incidentes y respuesta de emergencia."""

    def __init__(
        self,
        reactor: Reactor,
        safety_system: SafetySystem,
    ) -> None:
        self.reactor = reactor
        self.safety_system = safety_system
        self.controller = SafetyController(reactor)
        self.emergency_system = EmergencySystem(reactor)

        self._active_incidents: dict[str, Incident] = {}

    def evaluate(
        self,
        values: dict[str, float],
        timestamp_s: float = 0.0,
    ) -> SafetyIntegrationState:
        """Evalúa la planta y aplica las respuestas de seguridad."""

        assessment = self.safety_system.evaluate(values)

        alarms: list[Alarm] = []
        incidents: list[Incident] = []

        for name, status in assessment.results.items():
            if status == "critical":
                alarms.append(
                    Alarm(
                        name=name,
                        severity="critical",
                        message=f"{name} ha superado el límite crítico.",
                    )
                )

                if name in self._active_incidents:
                    incidents.append(self._active_incidents[name])
                else:
                    incident = Incident(
                        timestamp_s=timestamp_s,
                        name=name,
                        severity="critical",
                        message=f"{name} ha superado el límite crítico.",
                        source="SafetySystem",
                    )

                    self._active_incidents[name] = incident
                    incidents.append(incident)
            elif status == "warning":
                alarms.append(
                    Alarm(
                        name=name,
                        severity="warning",
                        message=f"{name} ha superado el límite de aviso.",
                    )
                )

                if name in self._active_incidents:
                    incidents.append(self._active_incidents[name])
                else:
                    incident = Incident(
                        timestamp_s=timestamp_s,
                        name=name,
                        severity="warning",
                        message=f"{name} ha superado el límite de aviso.",
                        source="SafetySystem",
                    )

                    self._active_incidents[name] = incident
                    incidents.append(incident)
            elif name in self._active_incidents:
                active_incident = self._active_incidents.pop(name)

                resolved_incident = Incident(
                    timestamp_s=timestamp_s,
                    name=active_incident.name,
                    severity=active_incident.severity,
                    message=active_incident.message,
                    source=active_incident.source,
                    status="resolved",
                )

                incidents.append(resolved_incident)

        self.controller.apply(assessment)

        if assessment.overall_status == "critical":
            self.emergency_system.activate()

        return SafetyIntegrationState(
            assessment=assessment,
            alarms=tuple(alarms),
            incidents=tuple(incidents),
            emergency_active=self.emergency_system.state().active,
        )