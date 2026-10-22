import pytest

from nuclear_sim.thermal.thermal_model import ThermalModel


def test_thermal_model_initial_temperature():
    model = ThermalModel()

    state = model.step(
        thermal_power_mw=0.0,
        heat_removed_mw=0.0,
        dt_s=0.0,
    )

    assert state.temperature_k == pytest.approx(573.15)


def test_heating_increases_temperature():
    model = ThermalModel(
        initial_temperature_k=573.15,
        thermal_capacity_mj_per_k=1000.0,
    )

    state = model.step(
        thermal_power_mw=100.0,
        heat_removed_mw=0.0,
        dt_s=10.0,
    )

    assert state.temperature_k == pytest.approx(574.15)


def test_heat_removal_decreases_temperature():
    model = ThermalModel(
        initial_temperature_k=573.15,
        thermal_capacity_mj_per_k=1000.0,
    )

    state = model.step(
        thermal_power_mw=0.0,
        heat_removed_mw=100.0,
        dt_s=10.0,
    )

    assert state.temperature_k == pytest.approx(572.15)


def test_balanced_power_keeps_temperature_constant():
    model = ThermalModel(
        initial_temperature_k=573.15,
        thermal_capacity_mj_per_k=1000.0,
    )

    state = model.step(
        thermal_power_mw=100.0,
        heat_removed_mw=100.0,
        dt_s=10.0,
    )

    assert state.temperature_k == pytest.approx(573.15)


def test_energy_balance():
    model = ThermalModel(
        initial_temperature_k=500.0,
        thermal_capacity_mj_per_k=1000.0,
    )

    state = model.step(
        thermal_power_mw=200.0,
        heat_removed_mw=50.0,
        dt_s=20.0,
    )

    expected_temperature = 500.0 + (150.0 * 20.0) / 1000.0

    assert state.temperature_k == pytest.approx(expected_temperature)


def test_negative_thermal_power_is_rejected():
    model = ThermalModel()

    with pytest.raises(ValueError):
        model.step(
            thermal_power_mw=-1.0,
            heat_removed_mw=0.0,
            dt_s=1.0,
        )


def test_negative_heat_removal_is_rejected():
    model = ThermalModel()

    with pytest.raises(ValueError):
        model.step(
            thermal_power_mw=0.0,
            heat_removed_mw=-1.0,
            dt_s=1.0,
        )


def test_negative_time_is_rejected():
    model = ThermalModel()

    with pytest.raises(ValueError):
        model.step(
            thermal_power_mw=100.0,
            heat_removed_mw=0.0,
            dt_s=-1.0,
        )


def test_invalid_thermal_capacity_is_rejected():
    with pytest.raises(ValueError):
        ThermalModel(
            thermal_capacity_mj_per_k=0.0,
        )