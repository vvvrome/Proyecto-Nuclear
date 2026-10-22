import math
import pytest

from nuclear_sim.radiation.radiation_field import RadiationField


def test_inverse_square_law():
    field = RadiationField()
    one = field.calculate(1000.0, 1.0, 1.0)
    two = field.calculate(1000.0, 1.0, 2.0)
    assert two.initial_rate == pytest.approx(one.initial_rate / 4.0)


def test_emission_probability_scales_rate():
    field = RadiationField()
    full = field.calculate(1000.0, 1.0, 1.0)
    half = field.calculate(1000.0, 0.5, 1.0)
    assert half.initial_rate == pytest.approx(full.initial_rate / 2.0)


def test_attenuation_reduces_rate():
    field = RadiationField(2.0)
    state = field.calculate(1000.0, 1.0, 1.0)
    assert state.attenuated_rate < state.initial_rate


def test_invalid_distance_is_rejected():
    with pytest.raises(ValueError):
        RadiationField().calculate(1000.0, 1.0, 0.0)
