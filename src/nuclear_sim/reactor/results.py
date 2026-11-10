from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import openmc


@dataclass(frozen=True)
class OpenMCResult:
    statepoint_path: Path
    keff: float
    keff_std_dev: float
    batches: int
    particles: int


def read_statepoint(statepoint_path: str | Path) -> OpenMCResult:
    path = Path(statepoint_path)

    if not path.exists():
        raise FileNotFoundError(f"Statepoint not found: {path}")

    with openmc.StatePoint(str(path)) as statepoint:
        keff = statepoint.keff

        return OpenMCResult(
            statepoint_path=path,
            keff=float(keff.nominal_value),
            keff_std_dev=float(keff.std_dev),
            batches=int(statepoint.n_batches),
            particles=int(statepoint.n_particles),
        )
