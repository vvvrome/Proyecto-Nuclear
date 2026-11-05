from dataclasses import dataclass


@dataclass(frozen=True)
class OpenMCResult:
    """Resultado básico de una simulación OpenMC."""

    keff: float
    keff_uncertainty: float
    statepoint_path: str
