import pytest

from nuclear_sim.thermal.coolant import Coolant
from nuclear_sim.thermal.generator import Generator
from nuclear_sim.thermal.heat_exchanger import HeatExchanger
from nuclear_sim.thermal.heat_transfer import HeatTransferModel
from nuclear_sim.thermal.power_cycle import PowerCycle
from nuclear_sim.thermal.steam_generator import SteamGenerator
from nuclear_sim.thermal.turbine import Turbine


def make_power_cycle() -> PowerCycle:
    coolant = Coolant(
        mass_flow_kg_s=1000.0,
        inlet_temperature_k=573.15,
        pressure_mpa=15.5,
    )

    heat_transfer = HeatTransferModel(
        efficiency=0.95,
    )

    heat_exchanger = HeatExchanger(
        overall_heat_transfer_coefficient_w_m2_k=1000.0,
        heat_transfer_area_m2=100.0,
    )

    steam_generator = SteamGenerator(
        efficiency=0.90,
        reference_temperature_k=373.15,
    )

    turbine = Turbine(
        efficiency=0.85,
    )

    generator = Generator(
        efficiency=0.98,
    )

    return PowerCycle(
        coolant=coolant,
        heat_transfer=heat_transfer,
        steam_generator=steam_generator,
        turbine=turbine,
        generator=generator,
        heat_exchanger=heat_exchanger,
    )


def test_power_cycle_uses_heat_exchanger():
    cycle = make_power_cycle()

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=573.15,
    )

    assert state.heat_exchanger_power_mw > 0.0
    assert state.heat_exchanger_lmtd_k > 0.0


def test_heat_exchanger_power_is_not_greater_than_transferred_power():
    cycle = make_power_cycle()

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=573.15,
    )

    assert state.heat_exchanger_power_mw <= state.transferred_power_mw


def test_heat_exchanger_produces_steam_power():
    cycle = make_power_cycle()

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=573.15,
    )

    assert state.steam_power_mw > 0.0


def test_heat_exchanger_power_drives_turbine():
    cycle = make_power_cycle()

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=573.15,
    )

    assert state.mechanical_power_mw > 0.0
    assert state.turbine_speed_rpm > 0.0


def test_heat_exchanger_power_drives_generator():
    cycle = make_power_cycle()

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=573.15,
    )

    assert state.electrical_power_mw > 0.0


def test_zero_reactor_power_produces_zero_heat_exchanger_power():
    cycle = make_power_cycle()

    state = cycle.run(
        reactor_power_mw=0.0,
        primary_temperature_k=573.15,
    )

    assert state.heat_exchanger_power_mw == pytest.approx(0.0)
    assert state.steam_power_mw == pytest.approx(0.0)
    assert state.mechanical_power_mw == pytest.approx(0.0)
    assert state.electrical_power_mw == pytest.approx(0.0)


def test_higher_reactor_power_produces_more_electrical_power():
    cycle = make_power_cycle()

    low = cycle.run(
        reactor_power_mw=500.0,
        primary_temperature_k=573.15,
    )

    high = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=573.15,
    )

    
    assert high.electrical_power_mw > low.electrical_power_mw


def test_power_cycle_without_heat_exchanger_remains_compatible():
    coolant = Coolant(
        mass_flow_kg_s=1000.0,
        inlet_temperature_k=573.15,
        pressure_mpa=15.5,
    )

    cycle = PowerCycle(
        coolant=coolant,
        heat_transfer=HeatTransferModel(efficiency=0.95),
        steam_generator=SteamGenerator(
            efficiency=0.90,
            reference_temperature_k=573.15,
        ),
        turbine=Turbine(efficiency=0.85),
        generator=Generator(efficiency=0.98),
    )

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=573.15,
    )

    assert state.electrical_power_mw > 0.0
    assert state.heat_exchanger_power_mw == pytest.approx(
        state.transferred_power_mw
    )
    assert state.heat_exchanger_lmtd_k == pytest.approx(0.0)