
import json
import math

import pytest

from nuclear_sim.nuclear.decay_chain import simulate_decay_chain
from nuclear_sim.nuclear.nuclide_data import load_nuclides


def make_catalog(tmp_path):
    """Cadena A -> B, con B estable y una única rama."""
    document = {
        "schema_version": 1,
        "source": {"name": "Prueba analítica"},
        "nuclides": [
            {
                "name": "A",
                "atomic_number": 10,
                "mass_number": 20,
                "half_life_s": 10.0,
                "decay_energy_mev": 0.0,
                "branches": [
                    {
                        "daughter": "B",
                        "fraction": 1.0,
                        "mode": "beta_minus",
                    }
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
        ],
    }

    path = tmp_path / "analytical_nuclides.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return load_nuclides(path)


@pytest.mark.parametrize("time_s", [0.0, 1.0, 10.0, 50.0, 100.0])
def test_parent_matches_analytical_solution(tmp_path, time_s):
    catalog = make_catalog(tmp_path)
    initial_atoms = 1000.0
    half_life = 10.0
    decay_constant = math.log(2.0) / half_life

    result = simulate_decay_chain(
        catalog,
        {"A": initial_atoms},
        time_s,
    )

    expected_parent = initial_atoms * math.exp(
        -decay_constant * time_s
    )

    assert result["atoms"]["A"] == pytest.approx(
        expected_parent, rel=1e-7, abs=1e-8
    )


@pytest.mark.parametrize("time_s", [0.0, 1.0, 10.0, 50.0, 100.0])
def test_stable_daughter_matches_analytical_solution(tmp_path, time_s):
    catalog = make_catalog(tmp_path)
    initial_atoms = 1000.0
    half_life = 10.0
    decay_constant = math.log(2.0) / half_life

    result = simulate_decay_chain(
        catalog,
        {"A": initial_atoms},
        time_s,
    )

    expected_parent = initial_atoms * math.exp(
        -decay_constant * time_s
    )
    expected_daughter = initial_atoms - expected_parent

    assert result["atoms"]["B"] == pytest.approx(
        expected_daughter, rel=1e-7, abs=1e-8
    )


def test_activity_matches_analytical_solution(tmp_path):
    catalog = make_catalog(tmp_path)
    initial_atoms = 1000.0
    time_s = 25.0
    decay_constant = math.log(2.0) / 10.0

    result = simulate_decay_chain(
        catalog,
        {"A": initial_atoms},
        time_s,
    )

    expected_activity = (
        decay_constant
        * initial_atoms
        * math.exp(-decay_constant * time_s)
    )

    assert result["activities_bq"]["A"] == pytest.approx(
        expected_activity, rel=1e-7, abs=1e-8
    )
