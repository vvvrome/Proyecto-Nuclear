import pytest

from nuclear_sim.nuclear.kinetics.temperature_feedback import (
    TemperatureFeedback,
)
from nuclear_sim.plant.reactor import Reactor
from nuclear_sim.plant.reactor_dynamics import ReactorDynamics
from nuclear_sim.plant.simulation import PlantSimulation
from nuclear_sim.thermal.coolant import Coolant
from nuclear_sim.thermal.generator import Generator
from nuclear_sim.thermal.heat_transfer import HeatTransferModel
from nuclear_sim.thermal.power_cycle import PowerCycle
from nuclear_sim.thermal.steam_generator import SteamGenerator
from nuclear_sim.thermal.thermal_model import ThermalModel
from nuclear_sim.thermal.turbine import Turbine


def create_power_cycle() -> PowerCycle:
    """Crea un ciclo de potencia para las pruebas."""

    coolant = Coolant(
        mass_flow_kg_s=1000.0,
        inlet_temperature_k=573.15,
        pressure_mpa=15.5,
        specific_heat_kj_kg_k=4.18,
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


def create_dynamics(
    initial_temperature_k: float = 573.15,
) -> ReactorDynamics:
    """Crea una dinámica de reactor con feedback térmico explícito."""

    thermal = ThermalModel(
        initial_temperature_k=initial_temperature_k,
    )

    feedback = TemperatureFeedback(
        reference_temperature_k=573.15,
        temperature_coefficient_per_k=-1.0e-5,
    )

    return ReactorDynamics(
        rated_power_mw=100.0,
        thermal_model=thermal,
        temperature_feedback=feedback,
    )


def test_plant_can_use_reactor_dynamics():
    reactor = Reactor(
        rated_power_mw=100.0,
    )

    thermal = ThermalModel()

    dynamics = ReactorDynamics(
        rated_power_mw=100.0,
        thermal_model=thermal,
    )

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=thermal,
        reactor_dynamics=dynamics,
    )

    state = simulation.step(
        dt_s=0.001,
        heat_removed_mw=100.0,
    )

    assert state.time_s == pytest.approx(0.001)
    assert state.power_mw == pytest.approx(100.0)
    assert state.temperature_k == pytest.approx(
        thermal.temperature_k
    )


def test_plant_uses_dynamic_power():
    reactor = Reactor(
        rated_power_mw=100.0,
    )

    dynamics = create_dynamics()

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=dynamics.thermal_model,
        reactor_dynamics=dynamics,
    )

    state = simulation.step(
        dt_s=0.001,
        heat_removed_mw=100.0,
        external_reactivity=0.001,
    )

    assert state.power_mw > 100.0
    assert state.total_reactivity > 0.0


def test_plant_reports_temperature_feedback():
    reactor = Reactor(
        rated_power_mw=100.0,
    )

    dynamics = create_dynamics(
        initial_temperature_k=583.15,
    )

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=dynamics.thermal_model,
        reactor_dynamics=dynamics,
    )

    state = simulation.step(
        dt_s=0.001,
        heat_removed_mw=100.0,
    )

    assert state.temperature_k == pytest.approx(583.15)
    assert state.temperature_reactivity == pytest.approx(-1.0e-4)
    assert state.total_reactivity == pytest.approx(-1.0e-4)


def test_plant_combines_external_and_temperature_reactivity():
    reactor = Reactor(
        rated_power_mw=100.0,
    )

    dynamics = create_dynamics(
        initial_temperature_k=583.15,
    )

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=dynamics.thermal_model,
        reactor_dynamics=dynamics,
    )

    state = simulation.step(
        dt_s=0.001,
        heat_removed_mw=100.0,
        external_reactivity=0.001,
    )

    assert state.external_reactivity == pytest.approx(
        0.001
    )

    assert state.temperature_reactivity == pytest.approx(
        -1.0e-4
    )

    assert state.total_reactivity == pytest.approx(
        0.0009
    )


def test_plant_integrates_dynamic_reactor_with_power_cycle():
    reactor = Reactor(
        rated_power_mw=100.0,
    )

    dynamics = create_dynamics()

    power_cycle = create_power_cycle()

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=dynamics.thermal_model,
        power_cycle=power_cycle,
        reactor_dynamics=dynamics,
    )

    state = simulation.step(
        dt_s=0.001,
        heat_removed_mw=100.0,
    )


    assert state.electrical_power_mw == pytest.approx(
        69.79707
    )


def test_positive_reactivity_increases_electrical_power():
    reactor = Reactor(
        rated_power_mw=100.0,
    )

    dynamics = create_dynamics()

    power_cycle = create_power_cycle()

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=dynamics.thermal_model,
        power_cycle=power_cycle,
        reactor_dynamics=dynamics,
    )

    initial = simulation.step(
        dt_s=0.001,
        heat_removed_mw=100.0,
    )

    changed = simulation.step(
        dt_s=0.001,
        heat_removed_mw=100.0,
        external_reactivity=0.001,
    )

    assert changed.electrical_power_mw > (
        initial.electrical_power_mw
    )


def test_dynamic_plant_keeps_temperature_stable_when_heat_is_balanced():
    reactor = Reactor(
        rated_power_mw=100.0,
    )

    dynamics = create_dynamics()

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=dynamics.thermal_model,
        reactor_dynamics=dynamics,
    )

    initial_temperature = simulation.step(
        dt_s=0.001,
        heat_removed_mw=100.0,
    ).temperature_k

    state = simulation.step(
        dt_s=0.001,
        heat_removed_mw=100.0,
    )

    assert state.temperature_k == pytest.approx(
        initial_temperature
    )


def test_dynamic_plant_heats_when_removed_heat_is_insufficient():
    reactor = Reactor(
        rated_power_mw=100.0,
    )

    dynamics = create_dynamics()

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=dynamics.thermal_model,
        reactor_dynamics=dynamics,
    )

    initial_temperature = simulation.step(
        dt_s=0.001,
        heat_removed_mw=100.0,
    ).temperature_k

    state = simulation.step(
        dt_s=0.001,
        heat_removed_mw=50.0,
    )

    assert state.temperature_k > initial_temperature
    assert state.temperature_reactivity < 0.0


def test_dynamic_plant_scram_reduces_neutron_population():
    reactor = Reactor(
        rated_power_mw=100.0,
    )

    dynamics = create_dynamics()

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=dynamics.thermal_model,
        reactor_dynamics=dynamics,
    )

    initial_population = dynamics.state().neutron_population

    dynamics.scram()

    state = dynamics.state()

    assert initial_population > 0.0
    assert state.neutron_population == pytest.approx(0.0)
    assert state.power_mw == pytest.approx(0.0)