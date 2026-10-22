import math
import pytest

from nuclear_sim.radiation.shielding import ShieldingModel


def test_exponential_attenuation():
    state = ShieldingModel(2.0).calculate(100.0, 0.5)
    assert state.transmitted_intensity == pytest.approx(100.0 * math.exp(-1.0))


def test_zero_thickness_preserves_intensity():
    state = ShieldingModel(2.0).calculate(100.0, 0.0)
    assert state.transmitted_intensity == pytest.approx(100.0)


def test_zero_coefficient_preserves_intensity():
    state = ShieldingModel(0.0).calculate(100.0, 10.0)
    assert state.transmitted_intensity == pytest.approx(100.0)


def test_invalid_thickness_is_rejected():
    with pytest.raises(ValueError):
        ShieldingModel(1.0).calculate(100.0, -1.0)
