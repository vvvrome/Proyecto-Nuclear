import pytest

from nuclear_sim.thermal.turbine import Turbine


def test_default_turbine_efficiency():
    turbine = Turbine()

    state = turbine.expand(1000.0)

    assert state.steam_power_mw == pytest.approx(1000.0)
    assert state.mechanical_power_mw == pytest.approx(850.0)
    assert state.efficiency == pytest.approx(0.85)


def test_custom_efficiency():
    turbine = Turbine(efficiency=0.80)

    state = turbine.expand(1000.0)

    assert state.mechanical_power_mw == pytest.approx(800.0)


def test_turbine_reaches_rated_speed_with_steam():
    turbine = Turbine()

    state = turbine.expand(1000.0)

    assert state.rotational_speed_rpm == pytest.approx(3000.0)


def test_zero_steam_stops_turbine():
    turbine = Turbine()

    state = turbine.expand(0.0)

    assert state.mechanical_power_mw == pytest.approx(0.0)
    assert state.rotational_speed_rpm == pytest.approx(0.0)


def test_negative_steam_power_is_rejected():
    turbine = Turbine()

    with pytest.raises(ValueError):
        turbine.expand(-1.0)


def test_invalid_efficiency_is_rejected():
    with pytest.raises(ValueError):
        Turbine(efficiency=0.0)


def test_invalid_speed_is_rejected():
    with pytest.raises(ValueError):
        Turbine(rated_speed_rpm=0.0)