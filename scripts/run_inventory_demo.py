
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nuclear_sim.nuclear.inventory import Isotope, IsotopeInventory


inventory = IsotopeInventory()

# Cadena didáctica: A -> B -> C
# Las vidas medias y energías son ficticias.
inventory.add_isotope(
    Isotope(
        name="A",
        half_life_s=10.0,
        decay_energy_mev=1.0,
        daughter="B",
    ),
    initial_atoms=1e12,
)

inventory.add_isotope(
    Isotope(
        name="B",
        half_life_s=20.0,
        decay_energy_mev=0.5,
        daughter="C",
    ),
    initial_atoms=0.0,
)

inventory.add_isotope(
    Isotope(
        name="C",
        half_life_s=None,  # Isótopo estable
    ),
    initial_atoms=0.0,
)

for elapsed in (0, 10, 20, 50, 100):
    state = inventory.simulate(elapsed)

    print(f"\nTiempo: {elapsed} s")

    for name, atoms in state.atoms.items():
        print(
            f"  {name}: {atoms:.6e} átomos | "
            f"{state.activities_bq[name]:.6e} Bq"
        )

    print(f"  Actividad total: {state.total_activity_bq:.6e} Bq")
    print(f"  Energía acumulada: {state.cumulative_energy_j:.6e} J")
