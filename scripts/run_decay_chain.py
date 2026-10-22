
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nuclear_sim.nuclear.nuclide_data import load_nuclides
from nuclear_sim.nuclear.decay_chain import simulate_decay_chain


catalog = load_nuclides(ROOT / "data" / "nuclear" / "nuclides.json")

for elapsed in (0, 10, 20, 50, 100):
    result = simulate_decay_chain(
        catalog,
        initial_atoms={"A": 1e12},
        time_s=elapsed,
    )

    print(f"\nTiempo: {elapsed} s")

    for name, atoms in result["atoms"].items():
        print(
            f"{name}: {atoms:.6e} átomos, "
            f"{result['activities_bq'][name]:.6e} Bq"
        )

    print(f"Actividad total: {result['total_activity_bq']:.6e} Bq")
    print(f"Energía acumulada: {result['cumulative_energy_j']:.6e} J")
