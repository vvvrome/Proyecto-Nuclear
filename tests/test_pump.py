import pytest

from nuclear_sim.thermal.pump import Pump


def test_default_efficiency():
    pump = Pump()

    state = pump.pump(
        mass_flow_kg_s=1000.0,
        inlet_pressure_mpa=15.0,
        outlet_pressure_mpa=16.0,
        inlet_temperature_k=573.15,
    )

    assert state.efficiency == pytest.approx(0.85)


def test_pressure_difference():
    pump = Pump()

    state = pump.pump(
        mass_flow_kg_s=1000.0,
        inlet_pressure_mpa=15.0,
        outlet_pressure_mpa=16.0,
        inlet_temperature_k=573.15,
    )

    assert state.pressure_difference_mpa == pytest.approx(1.0)


def test_hydraulic_power():
    pump = Pump()

    state = pump.pump(
        mass_flow_kg_s=1000.0,
        inlet_pressure_mpa=15.0,
        outlet_pressure_mpa=16.0,
        inlet_temperature_k=573.15,
    )

    assert state.hydraulic_power_mw == pytest.approx(1.0)


def test_electrical_power():
    pump = Pump()

    state = pump.pump(
        mass_flow_kg_s=1000.0,
        inlet_pressure_mpa=15.0,
        outlet_pressure_mpa=16.0,
        inlet_temperature_k=573.15,
    )

    assert state.electrical_power_mw == pytest.approx(
        1.0 / 0.85
    )


def test_higher_pressure_requires_more_power():
    pump = Pump()

    low = pump.pump(
        mass_flow_kg_s=1000.0,
        inlet_pressure_mpa=15.0,
        outlet_pressure_mpa=16.0,
        inlet_temperature_k=573.15,
    )

    high = pump.pump(
        mass_flow_kg_s=1000.0,
        inlet_pressure_mpa=15.0,
        outlet_pressure_mpa=17.0,
        inlet_temperature_k=573.15,
    )

    assert high.hydraulic_power_mw > low.hydraulic_power_mw
    assert high.electrical_power_mw > low.electrical_power_mw


def test_higher_mass_flow_requires_more_power():
    pump = Pump()

    low = pump.pump(
        mass_flow_kg_s=500.0,
        inlet_pressure_mpa=15.0,
        outlet_pressure_mpa=16.0,
        inlet_temperature_k=573.15,
    )

    high = pump.pump(
        mass_flow_kg_s=1000.0,
        inlet_pressure_mpa=15.0,
        outlet_pressure_mpa=16.0,
        inlet_temperature_k=573.15,
    )

    assert high.hydraulic_power_mw > low.hydraulic_power_mw


def test_temperature_is_preserved():
    pump = Pump()

    state = pump.pump(
        mass_flow_kg_s=1000.0,
        inlet_pressure_mpa=15.0,
        outlet_pressure_mpa=16.0,
        inlet_temperature_k=573.15,
    )

    assert state.outlet_temperature_k == pytest.approx(
        573.15
    )


def test_invalid_mass_flow():
    pump = Pump()

    with pytest.raises(ValueError):
        pump.pump(
            mass_flow_kg_s=0.0,
            inlet_pressure_mpa=15.0,
            outlet_pressure_mpa=16.0,
            inlet_temperature_k=573.15,
        )


def test_invalid_pressure_order():
    pump = Pump()

    with pytest.raises(ValueError):
        pump.pump(
            mass_flow_kg_s=1000.0,
            inlet_pressure_mpa=16.0,
            outlet_pressure_mpa=15.0,
            inlet_temperature_k=573.15,
        )


def test_invalid_temperature():
    pump = Pump()

    with pytest.raises(ValueError):
        pump.pump(
            mass_flow_kg_s=1000.0,
            inlet_pressure_mpa=15.0,
            outlet_pressure_mpa=16.0,
            inlet_temperature_k=0.0,
        )


def test_invalid_efficiency():
    with pytest.raises(ValueError):
        Pump(efficiency=0.0)


def test_invalid_density():
    with pytest.raises(ValueError):
        Pump(fluid_density_kg_m3=0.0)