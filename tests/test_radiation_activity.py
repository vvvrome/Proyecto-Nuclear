import math
import pytest

from nuclear_sim.radiation.activity import ActivityModel


def test_activity_from_lambda_and_atoms():
    state = ActivityModel(0.1).calculate(1000.0)
    assert state.activity_bq == pytest.approx(100.0)


def test_half_life_gives_correct_decay_constant():
    model = ActivityModel.from_half_life(10.0)
    assert model.decay_constant_per_s == pytest.approx(math.log(2.0) / 10.0)


def test_remaining_atoms_follow_exponential_law():
    model = ActivityModel.from_half_life(10.0)
    remaining = model.remaining_atoms(1000.0, 10.0)
    assert remaining == pytest.approx(500.0)


def test_zero_time_preserves_atoms():
    model = ActivityModel.from_half_life(10.0)
    assert model.remaining_atoms(1000.0, 0.0) == pytest.approx(1000.0)


def test_invalid_half_life_is_rejected():
    with pytest.raises(ValueError):
        ActivityModel.from_half_life(0.0)
