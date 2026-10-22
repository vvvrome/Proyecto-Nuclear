
import json
import math
import pytest

from nuclear_sim.nuclear.decay_chain import simulate_decay_chain
from nuclear_sim.nuclear.nuclide_data import load_nuclides


def make_catalog(tmp_path):
    """Crea una cadena ficticia A -> B/C con datos controlados."""
    document = {
        "schema_version": 1,
        "source": {
            "name": "Numerical validation",
            "reference": "Datos ficticios para pruebas",
        },
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
                        "fraction": 0.7,
                        "mode": "beta_minus",
                    },
                    {
                        "daughter": "C",
                        "fraction": 0.3,
                        "mode": "beta_minus",
                    },
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

    path = tmp_path / "nuclides_validation.json"
    path.write_text(json.dumps(document), encoding="utf-8")

    return load_nuclides(path)


def test_atom_conservation_after_one_half_life(tmp_path):
    catalog = make_catalog(tmp_path)

    result = simulate_decay_chain(
        catalog,
        {"A": 1000.0},
        10.0,
    )

    total_atoms = sum(result["atoms"].values())

    assert total_atoms == pytest.approx(1000.0, rel=1e-8)


def test_daughters_match_branching_fractions_after_one_half_life(
    tmp_path,
):
    catalog = make_catalog(tmp_path)

    result = simulate_decay_chain(
        catalog,
        {"A": 1000.0},
        10.0,
    )

    assert result["atoms"]["A"] == pytest.approx(500.0, rel=1e-8)
    assert result["atoms"]["B"] == pytest.approx(350.0, rel=1e-8)
    assert result["atoms"]["C"] == pytest.approx(150.0, rel=1e-8)


def test_atom_populations_are_nonnegative(tmp_path):
    catalog = make_catalog(tmp_path)

    result = simulate_decay_chain(
        catalog,
        {"A": 1000.0},
        100.0,
    )

    for nuclide, atoms in result["atoms"].items():
        assert atoms >= -1e-8, (
            f"Se han obtenido {atoms} átomos para {nuclide}"
        )


def test_atom_balance_diagnostics_are_consistent(tmp_path):
    catalog = make_catalog(tmp_path)

    result = simulate_decay_chain(
        catalog,
        {"A": 1000.0},
        100.0,
    )

    assert result["initial_total_atoms"] == pytest.approx(1000.0)

    assert result["atom_balance_error"] == pytest.approx(
        result["final_total_atoms"]
        - result["initial_total_atoms"]
    )

    assert result["atom_balance_tolerance"] > 0
    assert result["atom_balance_ok"] is True


def test_activity_diagnostics_are_consistent(tmp_path):
    catalog = make_catalog(tmp_path)

    result = simulate_decay_chain(
        catalog,
        {"A": 1000.0},
        10.0,
    )

    for name, record in catalog.items():
        half_life = record["half_life_s"]

        if half_life is None:
            expected_activity = 0.0
        else:
            decay_constant = math.log(2.0) / half_life
            expected_activity = (
                decay_constant * result["atoms"][name]
            )

        assert result["activities_bq"][name] == pytest.approx(
            expected_activity,
            rel=1e-10,
            abs=1e-10,
        )

    assert result["total_activity_bq"] == pytest.approx(
        sum(result["activities_bq"].values()),
        rel=1e-12,
        abs=1e-12,
    )
