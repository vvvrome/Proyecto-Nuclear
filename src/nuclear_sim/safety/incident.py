from dataclasses import dataclass


@dataclass(frozen=True)
class Incident:
    """Incidente ocurrido durante la operación de la planta."""

    timestamp_s: float
    name: str
    severity: str
    message: str
    source: str
    status: str = "open"

    def __post_init__(self) -> None:
        if self.timestamp_s < 0:
            raise ValueError(
                "El timestamp del incidente no puede ser negativo."
            )

        if not self.name:
            raise ValueError(
                "El nombre del incidente no puede estar vacío."
            )

        if self.severity not in {"warning", "critical"}:
            raise ValueError(
                "La severidad debe ser 'warning' o 'critical'."
            )

        if not self.message:
            raise ValueError(
                "El mensaje del incidente no puede estar vacío."
            )

        if not self.source:
            raise ValueError(
                "La fuente del incidente no puede estar vacía."
            )

        if self.status not in {"open", "resolved"}:
            raise ValueError(
                "El estado debe ser 'open' o 'resolved'."
            )