
from dataclasses import dataclass
import math

import numpy as np
from scipy.integrate import solve_ivp

from nuclear_sim.nuclear.decay import MEV_TO_J


@dataclass(frozen=True)
class Isotope:
    """Propiedades de un isótopo del inventario."""

    name: str
    half_life_s: float | None
    decay_energy_mev: float = 0.0
    daughter: str | None = None

    def __post_init__(self):
        if not self.name:
            raise ValueError("El nombre del isótopo no puede estar vacío.")

        if self.half_life_s is not None:
            if (
                not math.isfinite(self.half_life_s)
                or self.half_life_s <= 0
            ):
                raise ValueError(
                    "La vida media debe ser positiva y finita."
                )

        if (
            not math.isfinite(self.decay_energy_mev)
            or self.decay_energy_mev < 0
        ):
            raise ValueError(
                "La energía de desintegración debe ser finita y no negativa."
            )

        if self.daughter == self.name:
            raise ValueError("Un isótopo no puede ser su propio hijo.")

    @property
    def decay_constant(self) -> float:
        if self.half_life_s is None:
            return 0.0

        return math.log(2.0) / self.half_life_s


@dataclass(frozen=True)
class InventoryState:
    """Resultados del inventario en un instante."""

    time_s: float
    atoms: dict[str, float]
    activities_bq: dict[str, float]
    total_activity_bq: float
    cumulative_energy_j: float


class IsotopeInventory:
    """Inventario de isótopos con cadenas lineales de desintegración."""

    def __init__(self):
        self._isotopes: dict[str, Isotope] = {}
        self._initial_atoms: dict[str, float] = {}

    def add_isotope(
        self,
        isotope: Isotope,
        initial_atoms: float = 0.0,
    ) -> None:
        if isotope.name in self._isotopes:
            raise ValueError(
                f"El isótopo {isotope.name} ya está registrado."
            )

        if (
            not math.isfinite(initial_atoms)
            or initial_atoms < 0
        ):
            raise ValueError(
                "La cantidad inicial debe ser finita y no negativa."
            )

        self._isotopes[isotope.name] = isotope
        self._initial_atoms[isotope.name] = float(initial_atoms)

    def _validate_chain(self) -> None:
        for isotope in self._isotopes.values():
            if isotope.daughter is not None:
                if isotope.daughter not in self._isotopes:
                    raise ValueError(
                        f"El hijo {isotope.daughter} de "
                        f"{isotope.name} no está registrado."
                    )

                if isotope.half_life_s is None:
                    raise ValueError(
                        f"El isótopo estable {isotope.name} "
                        "no puede tener un hijo de desintegración."
                    )

        # Una cadena lineal no puede contener ciclos.
        for start in self._isotopes:
            visited = set()
            current = start

            while current is not None:
                if current in visited:
                    raise ValueError(
                        "Se ha detectado un ciclo en la cadena."
                    )

                visited.add(current)
                current = self._isotopes[current].daughter

    def simulate(self, time_s: float) -> InventoryState:
        """Calcula el inventario tras time_s, desde el estado inicial."""

        if not math.isfinite(time_s) or time_s < 0:
            raise ValueError(
                "El tiempo debe ser finito y no negativo."
            )

        self._validate_chain()

        names = list(self._isotopes)
        index = {name: i for i, name in enumerate(names)}
        count = len(names)

        initial = np.zeros(count + 1, dtype=float)

        for name, atoms in self._initial_atoms.items():
            initial[index[name]] = atoms

        # La última variable representa la energía acumulada.
        def derivatives(_time, state):
            result = np.zeros(count + 1, dtype=float)
            energy_rate = 0.0

            for name, isotope in self._isotopes.items():
                i = index[name]
                decay_rate = isotope.decay_constant * state[i]

                result[i] -= decay_rate

                if isotope.daughter is not None:
                    result[index[isotope.daughter]] += decay_rate

                energy_rate += (
                    decay_rate
                    * isotope.decay_energy_mev
                    * MEV_TO_J
                )

            result[-1] = energy_rate
            return result

        if time_s == 0:
            final = initial
        else:
            solution = solve_ivp(
                derivatives,
                (0.0, time_s),
                initial,
                method="DOP853",
                rtol=1e-9,
                atol=1e-8,
            )

            if not solution.success:
                raise RuntimeError(
                    f"Falló la integración: {solution.message}"
                )

            final = solution.y[:, -1]

        atoms = {
            name: max(0.0, float(final[index[name]]))
            for name in names
        }

        activities = {
            name: self._isotopes[name].decay_constant * atoms[name]
            for name in names
        }

        return InventoryState(
            time_s=time_s,
            atoms=atoms,
            activities_bq=activities,
            total_activity_bq=sum(activities.values()),
            cumulative_energy_j=max(0.0, float(final[-1])),
        )
