import pytest

from nuclear_sim.thermal.thermal_losses import ThermalLossModel
from nuclear_sim.thermal.coolant import Coolant
from nuclear_sim.thermal.generator import Generator
from nuclear_sim.thermal.heat_transfer import HeatTransferModel
from nuclear_sim.thermal.power_cycle import PowerCycle
from nuclear_sim.thermal.steam_generator import SteamGenerator
from nuclear_sim.thermal.turbine import Turbine
from nuclear_sim.thermal.condenser import Condenser
from nuclear_sim.thermal.pump import Pump

def create_power_cycle():
    coolant = Coolant(
        mass_flow_kg_s=1000.0,
        inlet_temperature_k=573.15,
        pressure_mpa=15.5,
    )

    heat_transfer = HeatTransferModel(
        efficiency=0.95,
    )

    steam_generator = SteamGenerator(
        efficiency=0.90,
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
    )


def test_power_cycle_zero_power():
    cycle = create_power_cycle()

    state = cycle.run(
        reactor_power_mw=0.0,
        primary_temperature_k=573.15,
    )

    assert state.reactor_power_mw == pytest.approx(0.0)
    assert state.transferred_power_mw == pytest.approx(0.0)
    assert state.steam_power_mw == pytest.approx(0.0)
    assert state.mechanical_power_mw == pytest.approx(0.0)
    assert state.electrical_power_mw == pytest.approx(0.0)
    assert state.turbine_speed_rpm == pytest.approx(0.0)


def test_power_cycle_converts_thermal_to_electrical_power():
    cycle = create_power_cycle()

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=673.15,
    )

    assert state.reactor_power_mw == pytest.approx(1000.0)
    assert state.transferred_power_mw == pytest.approx(950.0)
    assert state.steam_power_mw == pytest.approx(837.9)
    assert state.mechanical_power_mw == pytest.approx(712.215)
    assert state.electrical_power_mw == pytest.approx(697.9707)


def test_power_cycle_heats_coolant():
    cycle = create_power_cycle()

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=673.15,
    )

    assert state.coolant_outlet_temperature_k > 573.15


def test_power_cycle_spins_turbine():
    cycle = create_power_cycle()

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=673.15,
    )

    assert state.turbine_speed_rpm == pytest.approx(3000.0)


def test_higher_reactor_power_produces_more_electricity():
    cycle = create_power_cycle()

    low = cycle.run(
        reactor_power_mw=500.0,
        primary_temperature_k=673.15,
    )

    high = cycle.run(
        reactor_power_mw=2000.0,
        primary_temperature_k=673.15,
    )

    assert high.electrical_power_mw > low.electrical_power_mw
    assert high.mechanical_power_mw > low.mechanical_power_mw


def test_energy_conversion_efficiency():
    cycle = create_power_cycle()

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=673.15,
    )

    efficiency = (
        state.electrical_power_mw
        / state.reactor_power_mw
    )

    assert efficiency == pytest.approx(
        0.95 * 0.98 * 0.90 * 0.85 * 0.98
    )

def test_power_cycle_with_condenser_rejects_heat():
    condenser = Condenser(efficiency=0.95)

    cycle = PowerCycle(
        coolant=Coolant(
            mass_flow_kg_s=1000.0,
            inlet_temperature_k=573.15,
            pressure_mpa=15.5,
        ),
        heat_transfer=HeatTransferModel(
            efficiency=0.95,
        ),
        steam_generator=SteamGenerator(
            efficiency=0.90,
        ),
        turbine=Turbine(
            efficiency=0.85,
        ),
        generator=Generator(
            efficiency=0.98,
        ),
        condenser=condenser,
    )

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=673.15,
    )

    assert state.rejected_heat_mw > 0.0
    assert state.condensed_heat_mw > 0.0

def test_power_cycle_with_condenser_lowers_steam_temperature():
    condenser = Condenser(efficiency=0.95)

    cycle = PowerCycle(
        coolant=Coolant(
            mass_flow_kg_s=1000.0,
            inlet_temperature_k=573.15,
            pressure_mpa=15.5,
        ),
        heat_transfer=HeatTransferModel(
            efficiency=0.95,
        ),
        steam_generator=SteamGenerator(
            efficiency=0.90,
        ),
        turbine=Turbine(
            efficiency=0.85,
        ),
        generator=Generator(
            efficiency=0.98,
        ),
        condenser=condenser,
    )

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=673.15,
    )

    assert state.condenser_outlet_temperature_k < 648.15

def test_power_cycle_without_condenser_keeps_zero_condenser_values():
    cycle = create_power_cycle()

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=673.15,
    )

    assert state.rejected_heat_mw == pytest.approx(0.0)
    assert state.condensed_heat_mw == pytest.approx(0.0)
    assert state.condenser_outlet_temperature_k == pytest.approx(0.0)

def test_power_cycle_with_pump_consumes_auxiliary_power():
    pump = Pump(efficiency=0.85)

    cycle = PowerCycle(
        coolant=Coolant(
            mass_flow_kg_s=1000.0,
            inlet_temperature_k=573.15,
            pressure_mpa=15.5,
        ),
        heat_transfer=HeatTransferModel(
            efficiency=0.95,
        ),
        steam_generator=SteamGenerator(
            efficiency=0.90,
        ),
        turbine=Turbine(
            efficiency=0.85,
        ),
        generator=Generator(
            efficiency=0.98,
        ),
        pump=pump,
    )

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=673.15,
    )

    assert state.pump_hydraulic_power_mw > 0.0
    assert state.pump_electrical_power_mw > 0.0

def test_net_power_is_lower_than_gross_power():
    pump = Pump(efficiency=0.85)

    cycle = PowerCycle(
        coolant=Coolant(
            mass_flow_kg_s=1000.0,
            inlet_temperature_k=573.15,
            pressure_mpa=15.5,
        ),
        heat_transfer=HeatTransferModel(
            efficiency=0.95,
        ),
        steam_generator=SteamGenerator(
            efficiency=0.90,
        ),
        turbine=Turbine(
            efficiency=0.85,
        ),
        generator=Generator(
            efficiency=0.98,
        ),
        pump=pump,
    )

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=673.15,
    )

    assert (
        state.net_electrical_power_mw
        < state.electrical_power_mw
    )

def test_net_power_equals_gross_minus_pump_consumption():
    pump = Pump(efficiency=0.85)

    cycle = PowerCycle(
        coolant=Coolant(
            mass_flow_kg_s=1000.0,
            inlet_temperature_k=573.15,
            pressure_mpa=15.5,
        ),
        heat_transfer=HeatTransferModel(
            efficiency=0.95,
        ),
        steam_generator=SteamGenerator(
            efficiency=0.90,
        ),
        turbine=Turbine(
            efficiency=0.85,
        ),
        generator=Generator(
            efficiency=0.98,
        ),
        pump=pump,
    )

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=673.15,
    )

    assert state.net_electrical_power_mw == pytest.approx(
        state.electrical_power_mw
        - state.pump_electrical_power_mw
    )

def test_zero_power_produces_zero_auxiliary_power():
    pump = Pump(efficiency=0.85)

    cycle = PowerCycle(
        coolant=Coolant(
            mass_flow_kg_s=1000.0,
            inlet_temperature_k=573.15,
            pressure_mpa=15.5,
        ),
        heat_transfer=HeatTransferModel(
            efficiency=0.95,
        ),
        steam_generator=SteamGenerator(
            efficiency=0.90,
        ),
        turbine=Turbine(
            efficiency=0.85,
        ),
        generator=Generator(
            efficiency=0.98,
        ),
        pump=pump,
    )

    state = cycle.run(
        reactor_power_mw=0.0,
        primary_temperature_k=573.15,
    )

    assert state.pump_hydraulic_power_mw == pytest.approx(
        0.0
    )

    assert state.pump_electrical_power_mw == pytest.approx(
        0.0
    )

    assert state.net_electrical_power_mw == pytest.approx(
        0.0
    )

def test_power_cycle_reports_thermal_losses():
    cycle = create_power_cycle()

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=673.15,
    )

    assert state.lost_thermal_power_mw > 0.0


def test_power_cycle_useful_power_is_lower_than_transferred():
    cycle = create_power_cycle()

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=673.15,
    )

    assert (
        state.useful_thermal_power_mw
        < state.transferred_power_mw
    )


def test_power_cycle_thermal_balance():
    cycle = create_power_cycle()

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=673.15,
    )

    assert (
        state.useful_thermal_power_mw
        + state.lost_thermal_power_mw
    ) == pytest.approx(
        state.transferred_power_mw
    )


def test_power_cycle_custom_thermal_losses():
    cycle = PowerCycle(
        coolant=Coolant(
            mass_flow_kg_s=1000.0,
            inlet_temperature_k=573.15,
            pressure_mpa=15.5,
        ),
        heat_transfer=HeatTransferModel(),
        steam_generator=SteamGenerator(),
        turbine=Turbine(),
        generator=Generator(),
        thermal_losses=ThermalLossModel(
            loss_fraction=0.10,
        ),
    )

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=673.15,
    )

    assert state.lost_thermal_power_mw == pytest.approx(
        95.0
    )

    assert state.useful_thermal_power_mw == pytest.approx(
        855.0
    )

def test_power_cycle_energy_balance_is_available():
    cycle = PowerCycle(
        coolant=Coolant(
            mass_flow_kg_s=1000.0,
            inlet_temperature_k=573.15,
            pressure_mpa=15.5,
        ),
        heat_transfer=HeatTransferModel(),
        steam_generator=SteamGenerator(),
        turbine=Turbine(),
        generator=Generator(),
        condenser=Condenser(),
        pump=Pump(),
    )

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=673.15,
    )

    assert state.energy_balance is not None


def test_power_cycle_energy_balance_closes():
    cycle = PowerCycle(
        coolant=Coolant(
            mass_flow_kg_s=1000.0,
            inlet_temperature_k=573.15,
            pressure_mpa=15.5,
        ),
        heat_transfer=HeatTransferModel(),
        steam_generator=SteamGenerator(),
        turbine=Turbine(),
        generator=Generator(),
        condenser=Condenser(),
        pump=Pump(),
    )

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=673.15,
    )

    assert state.energy_balance is not None

    assert state.energy_balance.balance_error_mw == pytest.approx(
        0.0
    )


def test_power_cycle_energy_balance_net_efficiency():
    cycle = PowerCycle(
        coolant=Coolant(
            mass_flow_kg_s=1000.0,
            inlet_temperature_k=573.15,
            pressure_mpa=15.5,
        ),
        heat_transfer=HeatTransferModel(),
        steam_generator=SteamGenerator(),
        turbine=Turbine(),
        generator=Generator(),
        condenser=Condenser(),
        pump=Pump(),
    )

    state = cycle.run(
        reactor_power_mw=1000.0,
        primary_temperature_k=673.15,
    )

    assert state.energy_balance is not None

    assert (
        state.energy_balance.net_efficiency
        < state.energy_balance.thermal_efficiency
    )