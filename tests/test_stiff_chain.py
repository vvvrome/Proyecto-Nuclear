
import json
import math

import pytest

from nuclear_sim.nuclear.decay_chain import simulate_decay_chain
from nuclear_sim.nuclear.nuclide_data import load_nuclides


def make_catalog(tmp_path):
    document = {
        "schema_version": 1,
        "source": {"name": "Prueba de estabilidad numérica"},
        "nuclides": [
            {
                "name": "A",
                "atomic_number": 10,
                "mass_number": 20,
                "half_life_s": 1.0,
                "decay_energy_mev": 0.0,
                "branches": [
                    {"daughter": "B", "fraction": 1.0, "mode": "beta_minus"}
                ],
            },
            {
                "name": "B",
                "atomic_number": 11,
                "mass_number": 20,
                "half_life_s": 100000.0,
                "decay_energy_mev": 0.0,
                "branches": [
                    {"daughter": "C", "fraction": 1.0, "mode": "beta_minus"}
                ],
            },
            {
                "name": "C",
                "atomic_number": 12,
                "mass_number": 20,
                "half_life_s": None,
                "decay_energy_mev": 0.0,
                "branches": [],
            },
        ],
    }

    path = tmp_path / "stiff_nuclides.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return load_nuclides(path)


def test_chain_with_very_different_half_lives(tmp_path):
    catalog = make_catalog(tmp_path)

    n0_a = 1000.0
    time_s = 100.0
    lambda_a = math.log(2.0) / 1.0
    lambda_b = math.log(2.0) / 100000.0

    result = simulate_decay_chain(
        catalog,
        {"A": n0_a},
        time_s,
    )

    expected_a = n0_a * math.exp(-lambda_a * time_s)

    expected_b = (
        n0_a
        * lambda_a
        / (lambda_b - lambda_a)
        * (
            math.exp(-lambda_a * time_s)
            - math.exp(-lambda_b * time_s)
        )
    )

    expected_c = n0_a - expected_a - expected_b

    assert result["atoms"]["A"] == pytest.approx(
        expected_a, rel=1e-6, abs=1e-8
    )
    assert result["atoms"]["B"] == pytest.approx(
        expected_b, rel=1e-6, abs=1e-5
    )
    assert result["atoms"]["C"] == pytest.approx(
        expected_c, rel=1e-6, abs=1e-5
    )
    assert result["atom_balance_ok"] is True


def test_long_simulation_remains_finite(tmp_path):
    catalog = make_catalog(tmp_path)

    result = simulate_decay_chain(
        catalog,
        {"A": 1000.0},
        1_000_000.0,
    )
    print(
        f"\nEvaluaciones: {result['solver_nfev']}"
        f"\nJacobianos: {result['solver_njev']}"
        f"\nFactorizaciones LU: {result['solver_nlu']}"
    )
    assert all(
        math.isfinite(value)
        for value in result["atoms"].values()
    )
    assert all(value >= 0 for value in result["atoms"].values())
    assert result["atom_balance_ok"] is True
