import json

import pytest

from nuclear_sim.nuclear.nuclide_data import load_nuclides, validate_transition
from nuclear_sim.nuclear.decay_chain import simulate_decay_chain


def make_catalog(tmp_path):
    data = {
        "schema_version": 1,
        "source": {"name": "Prueba", "reference": "Datos ficticios"},
        "nuclides": [
            {
                "name": "A",
                "atomic_number": 10,
                "mass_number": 20,
                "half_life_s": 10.0,
                "decay_energy_mev": 1.0,
                "branches": [
                    {"daughter": "B", "fraction": 0.7, "mode": "beta_minus"},
                    {"daughter": "C", "fraction": 0.3, "mode": "beta_plus"},
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
                "atomic_number": 9,
                "mass_number": 20,
                "half_life_s": None,
                "decay_energy_mev": 0.0,
                "branches": [],
            },
        ],
    }
    path = tmp_path / "nuclides.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return load_nuclides(path)


def test_parent_halves_after_one_half_life(tmp_path):
    catalog = make_catalog(tmp_path)
    result = simulate_decay_chain(catalog, {"A": 1000.0}, 10.0)
    assert result["atoms"]["A"] == pytest.approx(500.0)


def test_branching_fractions_are_respected(tmp_path):
    catalog = make_catalog(tmp_path)
    result = simulate_decay_chain(catalog, {"A": 1000.0}, 1000.0)
    assert result["atoms"]["B"] == pytest.approx(700.0)
    assert result["atoms"]["C"] == pytest.approx(300.0)


def test_unknown_initial_isotope_is_rejected(tmp_path):
    catalog = make_catalog(tmp_path)
    with pytest.raises(ValueError):
        simulate_decay_chain(catalog, {"Unknown": 100.0}, 10.0)


def test_branch_fractions_must_sum_to_one(tmp_path):
    document = {
        "schema_version": 1,
        "source": {"name": "Test"},
        "nuclides": [
            {
                "name": "A",
                "atomic_number": 10,
                "mass_number": 20,
                "half_life_s": 10.0,
                "decay_energy_mev": 1.0,
                "branches": [
                    {"daughter": "B", "fraction": 0.4, "mode": "beta_minus"}
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
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ValueError):
        load_nuclides(path)


def test_beta_minus_preserves_mass_number_and_increases_z():
    parent = {"name": "Parent", "atomic_number": 10, "mass_number": 20}
    daughter = {"name": "Daughter", "atomic_number": 11, "mass_number": 20}
    validate_transition(parent, daughter, "beta_minus")


def test_alpha_decay_reduces_z_by_two_and_a_by_four():
    parent = {"name": "Parent", "atomic_number": 10, "mass_number": 20}
    daughter = {"name": "Daughter", "atomic_number": 8, "mass_number": 16}
    validate_transition(parent, daughter, "alpha")


def test_inconsistent_transition_is_rejected():
    parent = {"name": "Parent", "atomic_number": 10, "mass_number": 20}
    daughter = {"name": "Daughter", "atomic_number": 12, "mass_number": 20}
    with pytest.raises(ValueError):
        validate_transition(parent, daughter, "beta_minus")


def test_unknown_decay_mode_is_rejected():
    parent = {"name": "Parent", "atomic_number": 10, "mass_number": 20}
    daughter = {"name": "Daughter", "atomic_number": 11, "mass_number": 20}
    with pytest.raises(ValueError):
        validate_transition(parent, daughter, "unknown_mode")