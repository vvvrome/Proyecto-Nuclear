from dataclasses import dataclass

from nuclear_sim.safety.limits import SafetyLimit


@dataclass(frozen=True)
class SafetyAssessment:
    """Resultado de la evaluación de seguridad."""

    overall_status: str
    results: dict[str, str]


class SafetySystem:
    """Gestiona los límites de seguridad de la planta."""

    def __init__(self) -> None:
        self._limits: dict[str, SafetyLimit] = {}

    def add_limit(self, limit: SafetyLimit) -> None:
        """Registra un límite de seguridad."""

        if limit.name in self._limits:
            raise ValueError(
                f"Ya existe un límite llamado '{limit.name}'."
            )

        self._limits[limit.name] = limit

    def evaluate(self, values: dict[str, float]) -> SafetyAssessment:
        """Evalúa todas las variables de seguridad."""

        results: dict[str, str] = {}

        for name, limit in self._limits.items():
            if name not in values:
                raise KeyError(
                    f"No se ha proporcionado un valor para '{name}'."
                )

            results[name] = limit.evaluate(values[name])

        if "critical" in results.values():
            overall_status = "critical"
        elif "warning" in results.values():
            overall_status = "warning"
        else:
            overall_status = "normal"

        return SafetyAssessment(
            overall_status=overall_status,
            results=results,
        )

    def limit_count(self) -> int:
        """Devuelve el número de límites registrados."""

        return len(self._limits)