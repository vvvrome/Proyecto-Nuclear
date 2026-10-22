
from pathlib import Path

from nuclear_sim.nuclear.nuclide_data import load_nuclides


ROOT = Path(__file__).resolve().parents[1]
catalog_path = ROOT / "data" / "nuclear" / "nuclides.json"

catalog = load_nuclides(catalog_path)

print(f"Se han cargado {len(catalog)} núclidos:\n")

for name, isotope in catalog.items():
    state = isotope["state"]
    atomic_number = isotope["atomic_number"]
    mass_number = isotope["mass_number"]

    print(
        f"{name}: estado={state}, "
        f"Z={atomic_number}, A={mass_number}"
    )
