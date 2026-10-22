
import math
import pytest

from nuclear_sim.nuclear.decay import Nuclide, calculate_decay


def test_one_half_life_leaves_half_the_atoms():
    nuclide = Nuclide("Test", 100.0, 1.0)

    state = calculate_decay(nuclide, 1000.0, 100.0)

    assert state.remaining_atoms == pytest.approx(500.0)
    assert state.decayed_atoms == pytest.approx(500.0)


def test_activity_is_decay_constant_times_atoms():
    nuclide = Nuclide("Test", 100.0, 1.0)

    state = calculate_decay(nuclide, 1000.0, 0.0)

    expected = math.log(2) / 100.0 * 1000.0
    assert state.activity_bq == pytest.approx(expected)


def test_zero_time_releases_no_energy():
    nuclide = Nuclide("Test", 100.0, 1.0)

    state = calculate_decay(nuclide, 1000.0, 0.0)

    assert state.cumulative_energy_j == pytest.approx(0.0)


def test_negative_time_is_rejected():
    nuclide = Nuclide("Test", 100.0, 1.0)

    with pytest.raises(ValueError):
        calculate_decay(nuclide, 1000.0, -1.0)
