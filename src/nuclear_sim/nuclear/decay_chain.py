
import math

import numpy as np
from scipy.integrate import solve_ivp

from nuclear_sim.nuclear.decay import MEV_TO_J


def simulate_decay_chain(
    catalog: dict[str, dict],
    initial_atoms: dict[str, float],
    time_s: float,
    *,
    rtol: float = 1e-11,
    atol: float = 1e-10,
) -> dict:
    """Simula una cadena de desintegración radiactiva.

    rtol y atol controlan la precisión del integrador.

    La energía se calcula por rama cuando existen los datos necesarios.
    La conservación de núcleos se comprueba para cadenas en las que
    cada desintegración produce exactamente un núcleo hijo.
    """

    if (
        isinstance(time_s, bool)
        or not isinstance(time_s, (int, float))
        or not math.isfinite(time_s)
        or time_s < 0
    ):
        raise ValueError("El tiempo debe ser finito y no negativo.")

    for value, label in ((rtol, "rtol"), (atol, "atol")):
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value <= 0
        ):
            raise ValueError(f"{label} debe ser finito y positivo.")

    if not catalog:
        raise ValueError("El catálogo no puede estar vacío.")

    names = list(catalog)
    index = {name: i for i, name in enumerate(names)}
    count = len(names)

    for name, record in catalog.items():
        if record.get("half_life_s") is not None:
            half_life = record["half_life_s"]
            if (
                isinstance(half_life, bool)
                or not isinstance(half_life, (int, float))
                or not math.isfinite(half_life)
                or half_life <= 0
            ):
                raise ValueError(f"Vida media no válida para {name}.")

        branches = record.get("branches")
        if not isinstance(branches, list):
            raise ValueError(f"Ramas no válidas para {name}.")

        if record.get("half_life_s") is None and branches:
            raise ValueError(f"El núclido estable {name} tiene ramas.")

        for branch in branches:
            daughter = branch.get("daughter")
            fraction = branch.get("fraction")

            if daughter not in catalog:
                raise ValueError(
                    f"Hijo desconocido {daughter!r} en {name}."
                )

            if (
                isinstance(fraction, bool)
                or not isinstance(fraction, (int, float))
                or not math.isfinite(fraction)
                or not 0 < fraction <= 1
            ):
                raise ValueError(
                    f"Fracción de rama no válida en {name}."
                )

        if branches and not math.isclose(
            sum(branch["fraction"] for branch in branches),
            1.0,
            rel_tol=0.0,
            abs_tol=1e-8,
        ):
            raise ValueError(
                f"Las fracciones de las ramas de {name} deben sumar 1."
            )

    initial = np.zeros(count + 2, dtype=float)

    for name, atoms in initial_atoms.items():
        if name not in catalog:
            raise ValueError(f"Núclido desconocido: {name}")

        if (
            isinstance(atoms, bool)
            or not isinstance(atoms, (int, float))
            or not math.isfinite(atoms)
            or atoms < 0
        ):
            raise ValueError(f"Cantidad inicial no válida para {name}.")

        initial[index[name]] = atoms

    initial_total = float(sum(initial[:count]))

    lambdas = {}
    for name, record in catalog.items():
        half_life = record["half_life_s"]
        lambdas[name] = (
            0.0 if half_life is None else math.log(2.0) / half_life
        )

    energy_complete = True

    for record in catalog.values():
        if record["half_life_s"] is None:
            continue

        branches = record["branches"]

        if not branches:
            energy_complete = False

        for branch in branches:
            energy = branch.get("emitted_energy_mev")
            deposition = branch.get("deposition_fraction")

            if energy is None:
                energy_complete = False
            elif (
                isinstance(energy, bool)
                or not isinstance(energy, (int, float))
                or not math.isfinite(energy)
                or energy < 0
            ):
                raise ValueError("Energía emitida no válida.")

            if deposition is None:
                energy_complete = False
            elif (
                isinstance(deposition, bool)
                or not isinstance(deposition, (int, float))
                or not math.isfinite(deposition)
                or not 0 <= deposition <= 1
            ):
                raise ValueError("Fracción depositada no válida.")

    def derivatives(_time, state):
        result = np.zeros(count + 2, dtype=float)
        emitted_rate = 0.0
        deposited_rate = 0.0

        for name, record in catalog.items():
            decay_rate = lambdas[name] * state[index[name]]
            result[index[name]] -= decay_rate

            for branch in record["branches"]:
                branch_rate = decay_rate * branch["fraction"]
                result[index[branch["daughter"]]] += branch_rate

                energy = branch.get("emitted_energy_mev")
                deposition = branch.get("deposition_fraction")

                if energy is not None:
                    energy_rate = branch_rate * energy * MEV_TO_J
                    emitted_rate += energy_rate

                    if deposition is not None:
                        deposited_rate += energy_rate * deposition

        result[-2] = emitted_rate
        result[-1] = deposited_rate
        return result

    if time_s == 0:
        final = initial.copy()
        solver_success = True
        solver_message = "Tiempo cero: no se requiere integración."
        solver_nfev = 0
        solver_njev = 0
        solver_nlu = 0
    else:
        solution = solve_ivp(
            derivatives,
            (0.0, time_s),
            initial,
            method="BDF",
            rtol=rtol,
            atol=atol,
        
        )
        
        if not solution.success:
            raise RuntimeError(
                f"Falló la integración numérica: {solution.message}"
            )

        final = solution.y[:, -1]
        solver_success = solution.success
        solver_message = solution.message
        solver_nfev = solution.nfev
        solver_njev = solution.njev
        solver_nlu = solution.nlu

    if not np.all(np.isfinite(final)):
        raise RuntimeError(
            "La integración produjo valores NaN o infinitos."
        )

    raw_atoms = final[:count]
    negative_tolerance = max(atol * 10, 1e-12)

    if np.any(raw_atoms < -negative_tolerance):
        raise RuntimeError(
            "La integración produjo poblaciones negativas "
            "fuera de la tolerancia numérica."
        )

    atoms = {
        name: max(0.0, float(final[index[name]]))
        for name in names
    }

    final_total = float(sum(atoms.values()))
    conservation_error = final_total - initial_total

    # Un núcleo hijo por cada desintegración: el total se conserva.
    conservation_tolerance = max(
        10.0 * atol * count,
        10.0 * rtol * max(initial_total, 1.0),
    )
    conservation_ok = (
        abs(conservation_error) <= conservation_tolerance
    )

    activities = {
        name: lambdas[name] * atoms[name]
        for name in names
    }

    return {
        "time_s": time_s,
        "atoms": atoms,
        "activities_bq": activities,
        "total_activity_bq": sum(activities.values()),
        "cumulative_energy_j": max(0.0, float(final[-2])),
        "cumulative_emitted_energy_j": max(0.0, float(final[-2])),
        "cumulative_deposited_energy_j": max(0.0, float(final[-1])),
        "energy_complete": energy_complete,
        "solver_success": solver_success,
        "solver_message": solver_message,
        "rtol": rtol,
        "atol": atol,
        "initial_total_atoms": initial_total,
        "final_total_atoms": final_total,
        "atom_balance_error": conservation_error,
        "atom_balance_tolerance": conservation_tolerance,
        "atom_balance_ok": conservation_ok,
        "solver_nfev": solver_nfev,
        "solver_njev": solver_njev,
        "solver_nlu": solver_nlu,
    }
