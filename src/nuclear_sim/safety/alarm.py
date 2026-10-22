from dataclasses import dataclass


@dataclass(frozen=True)
class Alarm:
    """Alarma generada por una condición de seguridad."""

    name: str
    severity: str
    message: str
    active: bool = True

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("El nombre de la alarma no puede estar vacío.")

        if self.severity not in {"warning", "critical"}:
            raise ValueError(
                "La severidad debe ser 'warning' o 'critical'."
            )

        if not self.message:
            raise ValueError(
                "El mensaje de la alarma no puede estar vacío."
            )