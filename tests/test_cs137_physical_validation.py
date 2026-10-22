import math
from pathlib import Path

import pytest

from nuclear_sim.nuclear.decay_chain import simulate_decay_chain
from nuclear_sim.nuclear.nuclide_data import load_nuclides


CATALOG_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "nuclear"
    / "nuclides.json"
)

N0 = 1e12
CS_BRANCH_TO_BA137M = 0.947


@pytest.fixture
def catalog():
    return load_nuclides(CATALOG_PATH)


def test_cs137_population_matches_analytical_solution(catalog):
    """La población de Cs-137 debe seguir la ley exponencial."""
    time_s = 600.0

    result = simulate_decay_chain(
        catalog,
        {"Cs-137": N0},
        time_s,
    )

    half_life = catalog["Cs-137"]["half_life_s"]
    decay_constant = math.log(2.0) / half_life

    expected_atoms = N0 * math.exp(-decay_constant * time_s)

    assert result["atoms"]["Cs-137"] == pytest.approx(
        expected_atoms,
        rel=1e-7,
    )


def test_ba137m_population_matches_bateman_solution(catalog):
    """Comprueba la producción y desintegración del Ba-137m."""
    time_s = 600.0

    result = simulate_decay_chain(
        catalog,
        {"Cs-137": N0},
        time_s,
    )

    lambda_cs = (
        math.log(2.0) / catalog["Cs-137"]["half_life_s"]
    )
    lambda_ba = (
        math.log(2.0) / catalog["Ba-137m"]["half_life_s"]
    )

    expected_atoms = (
        N0
        * CS_BRANCH_TO_BA137M
        * lambda_cs
        / (lambda_ba - lambda_cs)
        * (
            math.exp(-lambda_cs * time_s)
            - math.exp(-lambda_ba * time_s)
        )
    )

    assert result["atoms"]["Ba-137m"] == pytest.approx(
        expected_atoms,
        rel=1e-5,
    )


def test_total_activity_matches_sum_of_nuclide_activities(catalog):
    """La actividad total debe ser la suma de las actividades."""
    result = simulate_decay_chain(
        catalog,
        {"Cs-137": N0},
        600.0,
    )

    expected_activity = sum(result["activities_bq"].values())

    assert result["total_activity_bq"] == pytest.approx(
        expected_activity,
        rel=1e-10,
    )

    for name in catalog:
        half_life = catalog[name]["half_life_s"]

        if half_life is None:
            expected = 0.0
        else:
            expected = (
                math.log(2.0)
                / half_life
                * result["atoms"][name]
            )

        assert result["activities_bq"][name] == pytest.approx(
            expected,
            rel=1e-10,
            abs=1e-12,
        )


def test_ba137m_approaches_expected_activity_ratio(catalog):
    """Tras un día, Ba-137m debe aproximarse al equilibrio."""
    result = simulate_decay_chain(
        catalog,
        {"Cs-137": N0},
        86400.0,
    )

    cs_activity = result["activities_bq"]["Cs-137"]
    ba_activity = result["activities_bq"]["Ba-137m"]

    assert cs_activity > 0.0

    assert ba_activity / cs_activity == pytest.approx(
        CS_BRANCH_TO_BA137M,
        abs=1e-5,
    )


def test_cs137_chain_preserves_total_number_of_nuclei(catalog):
    """Cada desintegración sustituye un núcleo por otro."""
    result = simulate_decay_chain(
        catalog,
        {"Cs-137": N0},
        86400.0,
    )

    assert result["final_total_atoms"] == pytest.approx(
        N0,
        rel=1e-8,
    )

    assert result["atom_balance_ok"] is True