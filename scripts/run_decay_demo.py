
from pathlib import Path
import sys

# Permite ejecutar el ejemplo desde la carpeta raíz del proyecto.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nuclear_sim.nuclear.decay import Nuclide, calculate_decay


# Ejemplo didáctico con Cs-137.
# Valores ilustrativos para comprobar el modelo.
cs137 = Nuclide(
    name="Cs-137",
    half_life_s=30.05 * 365.25 * 24 * 3600,
    decay_energy_mev=0.5,
)

initial_atoms = 1e20
elapsed_time = cs137.half_life_s

state = calculate_decay(cs137, initial_atoms, elapsed_time)

print(f"Radionúclido: {cs137.name}")
print(f"Tiempo: {state.time_s / (365.25 * 86400):.2f} años")
print(f"Núcleos iniciales: {initial_atoms:.6e}")
print(f"Núcleos restantes: {state.remaining_atoms:.6e}")
print(f"Núcleos desintegrados: {state.decayed_atoms:.6e}")
print(f"Actividad restante: {state.activity_bq:.6e} Bq")
print(f"Energía acumulada: {state.cumulative_energy_j:.6e} J")
