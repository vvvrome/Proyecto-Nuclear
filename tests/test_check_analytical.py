
import json
import math

import pytest

from nuclear_sim.nuclear.decay_chain import simulate_decay_chain
from nuclear_sim.nuclear.nuclide_data import load_nuclides


def make_catalog(tmp_path, half_life_a=10.0, half_life_b=20.0):
    """Cadena ficticia A -> B -> C, con C estable."""
    document = {
        "schema_version": 1,
        "source": {"name": "Validación analítica"},
        "nuclides": [
            {
                "name": "A",
                "atomic_number": 10,
                "mass_number": 20,
                "half_life_s": half_life_a,
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
                "half_life_s": half_life_b,
                "decay_energy_mev": 0.0,
                "branches": [
                    {
                        "daughter": "C",
                        "fraction": 1.0,
                        "mode": "beta_minus",
                    }
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

    path = tmp_path / "chain_nuclides.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return load_nuclides(path)


def analytical_atoms_a(n0, lambda_a, time_s):
    return n0 * math.exp(-lambda_a * time_s)


def analytical_atoms_b(n0_a, n0_b, lambda_a, lambda_b, time_s):
    if math.isclose(lambda_a, lambda_b, rel_tol=1e-12):
        # Caso de vidas medias iguales.
        return (
            n0_b * math.exp(-lambda_b * time_s)
            + n0_a * lambda_a * time_s
            * math.exp(-lambda_a * time_s)
        )

    return (
        n0_a
        * lambda_a
        / (lambda_b - lambda_a)
        * (
            math.exp(-lambda_a * time_s)
            - math.exp(-lambda_b * time_s)
        )
        + n0_b * math.exp(-lambda_b * time_s)
    )


@pytest.mark.parametrize("time_s", [0.0, 5.0, 10.0, 25.0, 60.0])
def test_two_step_chain_matches_analytical_solution(tmp_path, time_s):
    half_life_a = 10.0
    half_life_b = 20.0
    n0_a = 1000.0
    n0_b = 100.0

    catalog = make_catalog(
        tmp_path,
        half_life_a=half_life_a,
        half_life_b=half_life_b,
    )

    lambda_a = math.log(2.0) / half_life_a
    lambda_b = math.log(2.0) / half_life_b

    result = simulate_decay_chain(
        catalog,
        {"A": n0_a, "B": n0_b},
        time_s,
    )

    expected_a = analytical_atoms_a(n0_a, lambda_a, time_s)
    expected_b = analytical_atoms_b(
        n0_a, n0_b, lambda_a, lambda_b, time_s
    )
    expected_c = n0_a + n0_b - expected_a - expected_b

    assert result["atoms"]["A"] == pytest.approx(
        expected_a, rel=1e-7, abs=1e-8
    )
    assert result["atoms"]["B"] == pytest.approx(
        expected_b, rel=1e-7, abs=1e-8
    )
    assert result["atoms"]["C"] == pytest.approx(
        expected_c, rel=1e-7, abs=1e-8
    )


def test_intermediate_nuclide_initially_increases(tmp_path):
    catalog = make_catalog(tmp_path)

    result_early = simulate_decay_chain(
        catalog, {"A": 1000.0}, 5.0
    )
    result_later = simulate_decay_chain(
        catalog, {"A": 1000.0}, 15.0
    )

    assert result_early["atoms"]["B"] > 0
    assert result_later["atoms"]["B"] > result_early["atoms"]["B"]


def test_chain_conserves_total_atom_population(tmp_path):
    catalog = make_catalog(tmp_path)

    result = simulate_decay_chain(
        catalog, {"A": 1000.0, "B": 100.0}, 100.0
    )

    assert result["atom_balance_ok"] is True
    assert result["final_total_atoms"] == pytest.approx(
        1100.0, rel=1e-8
    )


def test_equal_half_lives_match_analytical_solution(tmp_path):
    half_life = 10.0
    n0_a = 1000.0
    n0_b = 0.0
    time_s = 10.0
    decay_constant = math.log(2.0) / half_life

    catalog = make_catalog(
        tmp_path,
        half_life_a=half_life,
        half_life_b=half_life,
    )

    result = simulate_decay_chain(
        catalog, {"A": n0_a, "B": n0_b}, time_s
    )

    expected_b = (
        n0_b * math.exp(-decay_constant * time_s)
        + n0_a * decay_constant * time_s
        * math.exp(-decay_constant * time_s)
    )

    assert result["atoms"]["B"] == pytest.approx(
        expected_b, rel=1e-7, abs=1e-8
    )
