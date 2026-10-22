from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ActivityState:
    """Actividad de un radionúclido."""

    atoms: float
    decay_constant_per_s: float
    activity_bq: float


class ActivityModel:
    """Modelo de actividad A(t) = lambda N(t)."""

    def __init__(self, decay_constant_per_s: float) -> None:
        if (
            not math.isfinite(decay_constant_per_s)
            or decay_constant_per_s < 0
        ):
            raise ValueError(
                "La constante de desintegración debe ser finita y no negativa."
            )

        self.decay_constant_per_s = float(decay_constant_per_s)

    @classmethod
    def from_half_life(cls, half_life_s: float) -> "ActivityModel":
        if not math.isfinite(half_life_s) or half_life_s <= 0:
            raise ValueError("La vida media debe ser positiva y finita.")

        return cls(math.log(2.0) / half_life_s)

    def remaining_atoms(self, initial_atoms: float, time_s: float) -> float:
        """Calcula N(t) = N0 exp(-lambda t)."""

        if not math.isfinite(initial_atoms) or initial_atoms < 0:
            raise ValueError("El número inicial de átomos debe ser válido.")

        if not math.isfinite(time_s) or time_s < 0:
            raise ValueError("El tiempo debe ser finito y no negativo.")

        return initial_atoms * math.exp(
            -self.decay_constant_per_s * time_s
        )

    def calculate(self, atoms: float) -> ActivityState:
        if not math.isfinite(atoms) or atoms < 0:
            raise ValueError(
                "El número de átomos debe ser finito y no negativo."
            )

        return ActivityState(
            atoms=atoms,
            decay_constant_per_s=self.decay_constant_per_s,
            activity_bq=self.decay_constant_per_s * atoms,
        )
