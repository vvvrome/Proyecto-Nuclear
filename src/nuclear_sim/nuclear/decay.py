
from dataclasses import dataclass
import math

SECONDS_PER_DAY = 86_400


@dataclass(frozen=True)
class Nuclide:
    """Propiedades básicas de un radionúclido."""

    name: str
    half_life_s: float
    decay_energy_mev: float

    def __post_init__(self):
        if not self.name:
            raise ValueError("El nombre no puede estar vacío.")

        if not math.isfinite(self.half_life_s) or self.half_life_s <= 0:
            raise ValueError("La vida media debe ser positiva y finita.")

        if not math.isfinite(self.decay_energy_mev) or self.decay_energy_mev < 0:
            raise ValueError("La energía debe ser finita y no negativa.")

    @property
    def decay_constant(self) -> float:
        return math.log(2) / self.half_life_s


@dataclass(frozen=True)
class DecayState:
    time_s: float
    remaining_atoms: float
    decayed_atoms: float
    activity_bq: float
    cumulative_energy_j: float


MEV_TO_J = 1.602176634e-13


def calculate_decay(
    nuclide: Nuclide,
    initial_atoms: float,
    time_s: float,
) -> DecayState:
    """Calcula la desintegración radiactiva ideal de un único núclido."""

    if not math.isfinite(initial_atoms) or initial_atoms < 0:
        raise ValueError("El número inicial de núcleos debe ser válido.")

    if not math.isfinite(time_s) or time_s < 0:
        raise ValueError("El tiempo debe ser finito y no negativo.")

    decay_constant = nuclide.decay_constant

    remaining = initial_atoms * math.exp(-decay_constant * time_s)
    decayed = initial_atoms - remaining
    activity = decay_constant * remaining

    energy_per_decay = nuclide.decay_energy_mev * MEV_TO_J
    cumulative_energy = decayed * energy_per_decay

    return DecayState(
        time_s=time_s,
        remaining_atoms=remaining,
        decayed_atoms=decayed,
        activity_bq=activity,
        cumulative_energy_j=cumulative_energy,
    )
