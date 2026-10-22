import pytest

from nuclear_sim.plant.plant_instrumentation import PlantInstrumentation
from nuclear_sim.plant.simulation import PlantState
from nuclear_sim.plant.simulation import PlantSimulation
from nuclear_sim.plant.reactor import Reactor
from nuclear_sim.thermal.thermal_model import ThermalModel
from nuclear_sim.thermal.power_cycle import PowerCycle
from nuclear_sim.thermal.coolant import Coolant
from nuclear_sim.thermal.heat_transfer import HeatTransferModel
from nuclear_sim.thermal.steam_generator import SteamGenerator
from nuclear_sim.thermal.turbine import Turbine
from nuclear_sim.thermal.generator import Generator

def create_state() -> PlantState:
    return PlantState(
        time_s=10.0,
        power_mw=1500.0,
        temperature_k=573.15,
        reactor_status="operating",
        electrical_power_mw=1000.0,
        auxiliary_power_mw=20.0,
        net_electrical_power_mw=980.0,
        external_reactivity=0.0001,
        temperature_reactivity=-0.00001,
        total_reactivity=0.00009,
    )


def test_plant_instrumentation_creates_sensors():
    instrumentation = PlantInstrumentation()

    assert instrumentation.system.sensor_count() == 17


def test_plant_instrumentation_creates_actuators():
    instrumentation = PlantInstrumentation()

    assert instrumentation.system.actuator_count() == 2


def test_plant_instrumentation_updates_sensors():
    instrumentation = PlantInstrumentation()

    state = create_state()

    instrumentation.update(state)

    power = instrumentation.system.get_sensor(
        "reactor_power"
    ).read()

    temperature = instrumentation.system.get_sensor(
        "reactor_temperature"
    ).read()

    assert power.value == pytest.approx(1500.0)
    assert temperature.value == pytest.approx(573.15)


def test_plant_instrumentation_preserves_timestamp():
    instrumentation = PlantInstrumentation()

    state = create_state()

    instrumentation.update(state)

    reading = instrumentation.system.get_sensor(
        "reactor_power"
    ).read()

    assert reading.timestamp_s == pytest.approx(10.0)


def test_plant_instrumentation_reads_reactivity():
    instrumentation = PlantInstrumentation()

    state = create_state()

    instrumentation.update(state)

    reading = instrumentation.system.get_sensor(
        "reactivity"
    ).read()

    assert reading.value == pytest.approx(0.00009)

def test_creates_expected_sensors():
    instrumentation = PlantInstrumentation()

    assert instrumentation.system.sensor_count() == 17

def test_updates_extended_sensor_values():
    instrumentation = PlantInstrumentation()

    state = PlantState(
        time_s=10.0,
        power_mw=3000.0,
        temperature_k=773.15,
        reactor_status="full_power",
        electrical_power_mw=697.9707,
        auxiliary_power_mw=5.0,
        net_electrical_power_mw=692.9707,
        neutron_population=1.0,
        transferred_power_mw=2850.0,
        lost_thermal_power_mw=57.0,
        useful_thermal_power_mw=2793.0,
        coolant_outlet_temperature_k=1239.15,
        steam_power_mw=2513.7,
        mechanical_power_mw=2136.645,
        turbine_speed_rpm=3000.0,
        rejected_heat_mw=377.055,
        condensed_heat_mw=358.20225,
        condenser_outlet_temperature_k=313.15,
        pump_hydraulic_power_mw=1.54,
        total_reactivity=0.001,
    )

    instrumentation.update(state)

    readings = instrumentation.sensor_readings()

    assert readings["neutron_population"].value == 1.0
    assert readings["transferred_power"].value == 2850.0
    assert readings["thermal_losses"].value == 57.0
    assert readings["steam_power"].value == 2513.7
    assert readings["turbine_speed"].value == 3000.0
    assert readings["rejected_heat"].value == 377.055
    assert readings["pump_hydraulic_power"].value == 1.54
    assert readings["reactivity"].value == 0.001

    assert readings["turbine_speed"].timestamp_s == 10.0

def test_plant_instrumentation_receives_simulation_state():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    thermal_model = ThermalModel()

    instrumentation = PlantInstrumentation()

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=thermal_model,
        instrumentation=instrumentation,
    )

    state = simulation.step(
        dt_s=10.0,
        heat_removed_mw=1000.0,
    )

    readings = instrumentation.sensor_readings()

    assert readings["reactor_power"].value == pytest.approx(
        state.power_mw
    )

    assert readings["reactor_temperature"].value == pytest.approx(
        state.temperature_k
    )

    assert readings["electrical_power"].value == pytest.approx(
        state.electrical_power_mw
    )

    assert readings["net_electrical_power"].value == pytest.approx(
        state.net_electrical_power_mw
    )

    assert readings["reactivity"].value == pytest.approx(
        state.total_reactivity
    )

    assert readings["reactor_power"].timestamp_s == pytest.approx(
        state.time_s
    )

def create_power_cycle():
    return PowerCycle(
        coolant=Coolant(
            mass_flow_kg_s=1000.0,
            inlet_temperature_k=573.15,
            pressure_mpa=15.5,
        ),
        heat_transfer=HeatTransferModel(),
        steam_generator=SteamGenerator(),
        turbine=Turbine(),
        generator=Generator(),
    )

def test_all_plant_sensors_match_simulation_state():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    thermal_model = ThermalModel()
    instrumentation = PlantInstrumentation()

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=thermal_model,
        power_cycle=create_power_cycle(),
        instrumentation=instrumentation,
    )

    state = simulation.step(
        dt_s=1.0,
        heat_removed_mw=1000.0,
    )

    readings = instrumentation.sensor_readings()

    expected_values = {
        "reactor_power": state.power_mw,
        "reactor_temperature": state.temperature_k,
        "neutron_population": state.neutron_population,
        "reactivity": state.total_reactivity,
        "transferred_power": state.transferred_power_mw,
        "thermal_losses": state.lost_thermal_power_mw,
        "useful_thermal_power": state.useful_thermal_power_mw,
        "coolant_outlet_temperature": state.coolant_outlet_temperature_k,
        "steam_power": state.steam_power_mw,
        "mechanical_power": state.mechanical_power_mw,
        "turbine_speed": state.turbine_speed_rpm,
        "electrical_power": state.electrical_power_mw,
        "net_electrical_power": state.net_electrical_power_mw,
        "rejected_heat": state.rejected_heat_mw,
        "condensed_heat": state.condensed_heat_mw,
        "condenser_outlet_temperature": state.condenser_outlet_temperature_k,
        "pump_hydraulic_power": state.pump_hydraulic_power_mw,
    }

    assert len(readings) == 17

    for name, expected in expected_values.items():
        assert readings[name].value == pytest.approx(expected)
        assert readings[name].timestamp_s == pytest.approx(state.time_s)