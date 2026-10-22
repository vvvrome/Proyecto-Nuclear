from dataclasses import dataclass
import math


@dataclass(frozen=True)
class DoseState:
    """Dosis absorbida y equivalente."""

    absorbed_energy_j: float
    mass_kg: float
    absorbed_dose_gy: float
    radiation_weighting_factor: float
    equivalent_dose_sv: float


class DoseModel:
    """D = E_abs/m y H = w_R D."""

    def __init__(self, radiation_weighting_factor: float = 1.0) -> None:
        if (
            not math.isfinite(radiation_weighting_factor)
            or radiation_weighting_factor <= 0
        ):
            raise ValueError(
                "El factor de ponderación debe ser positivo y finito."
            )

        self.radiation_weighting_factor = float(radiation_weighting_factor)

    def calculate(self, absorbed_energy_j: float, mass_kg: float) -> DoseState:
        if not math.isfinite(absorbed_energy_j) or absorbed_energy_j < 0:
            raise ValueError("La energía absorbida debe ser válida.")

        if not math.isfinite(mass_kg) or mass_kg <= 0:
            raise ValueError("La masa debe ser positiva y finita.")

        absorbed_dose = absorbed_energy_j / mass_kg
        equivalent_dose = absorbed_dose * self.radiation_weighting_factor

        return DoseState(
            absorbed_energy_j=absorbed_energy_j,
            mass_kg=mass_kg,
            absorbed_dose_gy=absorbed_dose,
            radiation_weighting_factor=self.radiation_weighting_factor,
            equivalent_dose_sv=equivalent_dose,
        )
