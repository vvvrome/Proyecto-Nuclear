from dataclasses import dataclass


@dataclass(frozen=True)
class SafetyLimit:
    """Límite de seguridad para una variable."""

    name: str
    warning: float
    critical: float

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError(
                "El nombre del límite no puede estar vacío."
            )

        if self.warning >= self.critical:
            raise ValueError(
                "El límite de warning debe ser menor que el crítico."
            )

    def evaluate(self, value: float) -> str:
        """Evalúa el nivel de seguridad de un valor."""

        if value >= self.critical:
            return "critical"

        if value >= self.warning:
            return "warning"

        return "normal"