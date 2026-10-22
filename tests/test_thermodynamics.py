import pytest

from nuclear_sim.thermal.thermodynamics import (
    convective_heat_rate,
    sensible_energy,
    temperature_change_from_energy,
)


def test_sensible_energy_q_equals_m_cp_delta_t():
    state = sensible_energy(10.0, 4180.0, 20.0)
    assert state.energy_j == pytest.approx(836000.0)


def test_temperature_change_is_inverse_energy_balance():
    delta_t = temperature_change_from_energy(836000.0, 10.0, 4180.0)
    assert delta_t == pytest.approx(20.0)


def test_negative_temperature_change_is_allowed():
    state = sensible_energy(10.0, 4180.0, -20.0)
    assert state.energy_j == pytest.approx(-836000.0)


def test_convective_heat_rate_qdot_equals_h_a_delta_t():
    state = convective_heat_rate(100.0, 2.0, 10.0)
    assert state.heat_rate_w == pytest.approx(2000.0)


def test_invalid_mass_is_rejected():
    with pytest.raises(ValueError):
        sensible_energy(0.0, 4180.0, 1.0)


def test_invalid_area_is_rejected():
    with pytest.raises(ValueError):
        convective_heat_rate(100.0, 0.0, 10.0)
