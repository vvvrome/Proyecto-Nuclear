
import json

import pytest

from nuclear_sim.nuclear.decay_chain import simulate_decay_chain
from nuclear_sim.nuclear.nuclide_data import load_nuclides


def make_catalog(tmp_path):
    document = {
        "schema_version": 1,
        "source": {"name": "Prueba"},
        "nuclides": [
            {
                "name": "A",
                "atomic_number": 10,
                "mass_number": 20,
                "half_life_s": 10.0,
                "decay_energy_mev": 0.0,
                "branches": [
                    {"daughter": "B", "fraction": 0.7, "mode": "beta_minus"},
                    {"daughter": "C", "fraction": 0.3, "mode": "beta_minus"},
                ],
            },
            {
                "name": "B",
                "atomic_number": 11,
                "mass_number": 20,
                "half_life_s": None,
                "decay_energy_mev": 0.0,
                "branches": [],
            },
            {
                "name": "C",
                "atomic_number": 11,
                "mass_number": 20,
                "half_life_s": None,
                "decay_energy_mev": 0.0,
                "branches": [],
            },
        ],
    }

    path = tmp_path / "nuclides.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return load_nuclides(path)


def test_solver_reports_atom_conservation(tmp_path):
    catalog = make_catalog(tmp_path)

    result = simulate_decay_chain(catalog, {"A": 1000.0}, 100.0)

    assert result["solver_success"] is True
    assert result["atom_balance_ok"] is True
    assert result["initial_total_atoms"] == pytest.approx(1000.0)
    assert result["final_total_atoms"] == pytest.approx(1000.0)
    assert abs(result["atom_balance_error"]) <= (
        result["atom_balance_tolerance"]
    )


def test_invalid_tolerances_are_rejected(tmp_path):
    catalog = make_catalog(tmp_path)

    with pytest.raises(ValueError):
        simulate_decay_chain(
            catalog, {"A": 1000.0}, 10.0, rtol=0
        )

    with pytest.raises(ValueError):
        simulate_decay_chain(
            catalog, {"A": 1000.0}, 10.0, atol=-1
        )
