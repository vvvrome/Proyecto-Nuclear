
import pytest

from nuclear_sim.nuclear.decay_chain import simulate_decay_chain
from nuclear_sim.nuclear.decay import MEV_TO_J


def test_energy_is_calculated_per_branch():
    catalog = {
        "A": {
            "half_life_s": 10.0,
            "decay_energy_mev": 0.0,
            "branches": [
                {
                    "daughter": "B",
                    "fraction": 0.5,
                    "mode": "beta_minus",
                    "emitted_energy_mev": 2.0,
                    "deposition_fraction": 0.5,
                },
                {
                    "daughter": "C",
                    "fraction": 0.5,
                    "mode": "beta_minus",
                    "emitted_energy_mev": 4.0,
                    "deposition_fraction": 1.0,
                },
            ],
        },
        "B": {
            "half_life_s": None,
            "decay_energy_mev": 0.0,
            "branches": [],
        },
        "C": {
            "half_life_s": None,
            "decay_energy_mev": 0.0,
            "branches": [],
        },
    }

    result = simulate_decay_chain(
        catalog,
        {"A": 1000.0},
        1000.0,
    )

    remaining = result["atoms"]["A"]
    decayed = 1000.0 - remaining
    expected_emitted = decayed *(0.5 * 2.0 + 0.5 * 4.0) * MEV_TO_J
    expected_deposited = decayed * (0.5 * 2.0 * 0.5 + 0.5 * 4.0 * 1.0) * MEV_TO_J

    assert result["cumulative_emitted_energy_j"] == pytest.approx(
        expected_emitted
    )
    assert result["cumulative_deposited_energy_j"] == pytest.approx(
        expected_deposited
    )
    assert result["energy_complete"] is True


def test_missing_energy_is_reported_as_incomplete():
    catalog = {
        "A": {
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
        "B": {
            "half_life_s": None,
            "decay_energy_mev": 0.0,
            "branches": [],
        },
    }

    result = simulate_decay_chain(catalog, {"A": 100.0}, 10.0)

    assert result["energy_complete"] is False



def test_emitted_energy_exceeds_deposited_energy():
    catalog = {
        "A": {
            "half_life_s": 10.0,
            "decay_energy_mev": 0.0,
            "branches": [
                {
                    "daughter": "B",
                    "fraction": 1.0,
                    "mode": "beta_minus",
                    "emitted_energy_mev": 2.0,
                    "deposition_fraction": 0.5,
                }
            ],
        },
        "B": {
            "half_life_s": None,
            "decay_energy_mev": 0.0,
            "branches": [],
        },
    }

    result = simulate_decay_chain(
        catalog,
        {"A": 1000.0},
        100.0,
    )

    assert result["energy_complete"] is True

    assert result["cumulative_emitted_energy_j"] >= (
        result["cumulative_deposited_energy_j"]
    )

    assert result["cumulative_emitted_energy_j"] >= 0.0
    assert result["cumulative_deposited_energy_j"] >= 0.0

    assert result["cumulative_deposited_energy_j"] == pytest.approx(
        result["cumulative_emitted_energy_j"] * 0.5,
        rel=1e-8,
    )


def test_zero_time_produces_zero_cumulative_energy():
    catalog = {
        "A": {
            "half_life_s": 10.0,
            "decay_energy_mev": 0.0,
            "branches": [
                {
                    "daughter": "B",
                    "fraction": 1.0,
                    "mode": "beta_minus",
                    "emitted_energy_mev": 2.0,
                    "deposition_fraction": 0.5,
                }
            ],
        },
        "B": {
            "half_life_s": None,
            "decay_energy_mev": 0.0,
            "branches": [],
        },
    }

    result = simulate_decay_chain(
        catalog,
        {"A": 1000.0},
        0.0,
    )

    assert result["cumulative_emitted_energy_j"] == pytest.approx(0.0)
    assert result["cumulative_deposited_energy_j"] == pytest.approx(0.0)
    assert result["atoms"]["A"] == pytest.approx(1000.0)
    assert result["energy_complete"] is True
