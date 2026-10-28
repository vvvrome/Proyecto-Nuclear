import pytest

from nuclear_sim.thermal.pump import Pump
from nuclear_sim.plant.reactor import Reactor
from nuclear_sim.plant.simulation import PlantSimulation
from nuclear_sim.thermal.thermal_model import ThermalModel
from nuclear_sim.thermal.coolant import Coolant
from nuclear_sim.thermal.generator import Generator
from nuclear_sim.thermal.heat_transfer import HeatTransferModel
from nuclear_sim.thermal.power_cycle import PowerCycle
from nuclear_sim.thermal.steam_generator import SteamGenerator
from nuclear_sim.thermal.turbine import Turbine
from nuclear_sim.thermal.condenser import Condenser
from nuclear_sim.thermal.pump import Pump
from nuclear_sim.plant.reactor_dynamics import ReactorDynamics
from nuclear_sim.plant.plant_instrumentation import PlantInstrumentation
from nuclear_sim.plant.simulation import PlantController
from nuclear_sim.plant.safety_integration import SafetyIntegration
from nuclear_sim.safety.limits import SafetyLimit
from nuclear_sim.safety.system import SafetySystem


def test_simulation_starts_at_zero_time():
    reactor = Reactor(rated_power_mw=3000)
    thermal = ThermalModel()
    simulation = PlantSimulation(reactor, thermal)

    state = simulation.step(
        dt_s=0.0,
        heat_removed_mw=0.0,
    )

    assert state.time_s == pytest.approx(0.0)


def test_simulation_uses_reactor_power():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(0.5)

    thermal = ThermalModel(
        initial_temperature_k=573.15,
        thermal_capacity_mj_per_k=1000.0,
    )

    simulation = PlantSimulation(reactor, thermal)

    state = simulation.step(
        dt_s=10.0,
        heat_removed_mw=0.0,
    )

    assert state.power_mw == pytest.approx(1500.0)


def test_simulation_heats_when_power_exceeds_heat_removal():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(0.5)

    thermal = ThermalModel(
        initial_temperature_k=573.15,
        thermal_capacity_mj_per_k=1000.0,
    )

    simulation = PlantSimulation(reactor, thermal)

    state = simulation.step(
        dt_s=10.0,
        heat_removed_mw=1000.0,
    )

    expected_temperature = 573.15 + (1500.0 - 1000.0) * 10.0 / 1000.0

    assert state.temperature_k == pytest.approx(expected_temperature)


def test_simulation_temperature_remains_constant_when_balanced():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(0.5)

    thermal = ThermalModel(
        initial_temperature_k=573.15,
        thermal_capacity_mj_per_k=1000.0,
    )

    simulation = PlantSimulation(reactor, thermal)

    state = simulation.step(
        dt_s=10.0,
        heat_removed_mw=1500.0,
    )

    assert state.temperature_k == pytest.approx(573.15)


def test_simulation_cools_when_heat_removal_exceeds_power():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(0.5)

    thermal = ThermalModel(
        initial_temperature_k=573.15,
        thermal_capacity_mj_per_k=1000.0,
    )

    simulation = PlantSimulation(reactor, thermal)

    state = simulation.step(
        dt_s=10.0,
        heat_removed_mw=2000.0,
    )

    expected_temperature = 573.15 + (1500.0 - 2000.0) * 10.0 / 1000.0

    assert state.temperature_k == pytest.approx(expected_temperature)


def test_simulation_time_accumulates():
    reactor = Reactor(rated_power_mw=3000)
    thermal = ThermalModel()
    simulation = PlantSimulation(reactor, thermal)

    simulation.step(
        dt_s=10.0,
        heat_removed_mw=0.0,
    )

    state = simulation.step(
        dt_s=5.0,
        heat_removed_mw=0.0,
    )

    assert state.time_s == pytest.approx(15.0)


def test_simulation_reports_reactor_status():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    thermal = ThermalModel()
    simulation = PlantSimulation(reactor, thermal)

    state = simulation.step(
        dt_s=1.0,
        heat_removed_mw=0.0,
    )

    assert state.reactor_status == "full_power"


def test_simulation_reflects_scram():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    thermal = ThermalModel()
    simulation = PlantSimulation(reactor, thermal)

    reactor.scram()

    state = simulation.step(
        dt_s=1.0,
        heat_removed_mw=0.0,
    )

    assert state.power_mw == pytest.approx(0.0)
    assert state.reactor_status == "shutdown"

def create_power_cycle():
    coolant = Coolant(
        mass_flow_kg_s=1000.0,
        inlet_temperature_k=573.15,
        pressure_mpa=15.5,
    )

    return PowerCycle(
        coolant=coolant,
        heat_transfer=HeatTransferModel(),
        steam_generator=SteamGenerator(),
        turbine=Turbine(),
        generator=Generator(),
    )

def create_power_cycle_with_pump():
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
        pump=Pump(),
    )

def test_plant_without_power_cycle_has_zero_electrical_power():
    reactor = Reactor(rated_power_mw=3000)
    thermal_model = ThermalModel()

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=thermal_model,
    )

    state = simulation.step(
        dt_s=1.0,
        heat_removed_mw=0.0,
    )

    assert state.electrical_power_mw == pytest.approx(0.0)


def test_plant_with_power_cycle_generates_electricity():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    thermal_model = ThermalModel()

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=thermal_model,
        power_cycle=create_power_cycle(),
    )

    state = simulation.step(
        dt_s=0.0,
        heat_removed_mw=0.0,
    )

    assert state.electrical_power_mw > 0.0


def test_plant_electrical_power_scales_with_reactor_power():
    reactor = Reactor(rated_power_mw=3000)
    thermal_model = ThermalModel()
    cycle = create_power_cycle()

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=thermal_model,
        power_cycle=cycle,
    )

    reactor.set_power_fraction(0.5)

    half_power = simulation.step(
        dt_s=0.0,
        heat_removed_mw=0.0,
    )

    reactor.set_power_fraction(1.0)

    full_power = simulation.step(
        dt_s=0.0,
        heat_removed_mw=0.0,
    )

    assert full_power.electrical_power_mw > (
        half_power.electrical_power_mw
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


def test_plant_without_power_cycle_has_zero_electrical_power():
    reactor = Reactor(rated_power_mw=3000)
    thermal_model = ThermalModel()

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=thermal_model,
    )

    state = simulation.step(
        dt_s=1.0,
        heat_removed_mw=0.0,
    )

    assert state.electrical_power_mw == pytest.approx(0.0)


def test_plant_with_power_cycle_generates_electricity():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
        power_cycle=create_power_cycle(),
    )

    state = simulation.step(
        dt_s=0.0,
        heat_removed_mw=0.0,
    )

    assert state.electrical_power_mw > 0.0


def test_electrical_power_scales_with_reactor_power():
    reactor = Reactor(rated_power_mw=3000)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
        power_cycle=create_power_cycle(),
    )

    reactor.set_power_fraction(0.5)

    half_power = simulation.step(
        dt_s=0.0,
        heat_removed_mw=0.0,
    )

    reactor.set_power_fraction(1.0)

    full_power = simulation.step(
        dt_s=0.0,
        heat_removed_mw=0.0,
    )

    assert full_power.electrical_power_mw > (
        half_power.electrical_power_mw
    )


def test_scrammed_reactor_produces_no_electricity():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
        power_cycle=create_power_cycle(),
    )

    reactor.scram()

    state = simulation.step(
        dt_s=0.0,
        heat_removed_mw=0.0,
    )

    assert state.electrical_power_mw == pytest.approx(0.0)
    assert state.reactor_status == "shutdown"

def test_plant_simulation_reports_gross_electrical_power():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
        power_cycle=create_power_cycle_with_pump(),
    )

    state = simulation.step(
        dt_s=0.0,
        heat_removed_mw=0.0,
    )

    assert state.electrical_power_mw > 0.0


def test_plant_simulation_reports_auxiliary_power():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
        power_cycle=create_power_cycle_with_pump(),
    )

    state = simulation.step(
        dt_s=0.0,
        heat_removed_mw=0.0,
    )

    assert state.auxiliary_power_mw > 0.0


def test_plant_simulation_net_power_is_lower_than_gross():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
        power_cycle=create_power_cycle_with_pump(),
    )

    state = simulation.step(
        dt_s=0.0,
        heat_removed_mw=0.0,
    )

    assert state.net_electrical_power_mw < state.electrical_power_mw


def test_plant_simulation_net_power_balance():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
        power_cycle=create_power_cycle_with_pump(),
    )

    state = simulation.step(
        dt_s=0.0,
        heat_removed_mw=0.0,
    )

    assert state.net_electrical_power_mw == pytest.approx(
        state.electrical_power_mw - state.auxiliary_power_mw
    )

def test_plant_simulation_exposes_energy_balance():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
        power_cycle=create_power_cycle(),
    )

    state = simulation.step(
        dt_s=0.0,
        heat_removed_mw=0.0,
    )

    assert state.energy_balance is not None

def test_plant_simulation_energy_balance_closes():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
        power_cycle=PowerCycle(
            coolant=Coolant(
                mass_flow_kg_s=1000.0,
                inlet_temperature_k=573.15,
                pressure_mpa=15.5,
            ),
            heat_transfer=HeatTransferModel(),
            steam_generator=SteamGenerator(),
            turbine=Turbine(),
            generator=Generator(),
            pump=Pump(),
            condenser=Condenser()
        ),
    )
    state = simulation.step(
        dt_s=0.0,
        heat_removed_mw=0.0,
    )
    

    assert state.energy_balance is not None
    assert state.energy_balance.balance_error_mw == pytest.approx(0.0)

def test_plant_simulation_net_efficiency_is_lower_than_thermal_efficiency():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
        power_cycle=PowerCycle(
            coolant=Coolant(
                mass_flow_kg_s=1000.0,
                inlet_temperature_k=573.15,
                pressure_mpa=15.5,
            ),
            heat_transfer=HeatTransferModel(),
            steam_generator=SteamGenerator(),
            turbine=Turbine(),
            generator=Generator(),
            pump=Pump(),
            condenser=Condenser()
        ),
    )

    state = simulation.step(
        dt_s=0.0,
        heat_removed_mw=0.0,
    )

    assert state.energy_balance is not None
    assert (
        state.energy_balance.net_efficiency
        < state.energy_balance.thermal_efficiency
    )

def test_full_power_operation_keeps_energy_balance_closed():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
        power_cycle=create_power_cycle(),
    )

    state = simulation.step(
        dt_s=0.0,
        heat_removed_mw=0.0,
    )

    assert state.power_mw == pytest.approx(3000.0)
    assert state.electrical_power_mw > 0.0
    assert state.energy_balance is not None
    assert state.energy_balance.balance_error_mw == pytest.approx(0.0)

def test_increased_heat_removal_reduces_temperature():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(0.5)

    thermal_model = ThermalModel(
        initial_temperature_k=573.15,
        thermal_capacity_mj_per_k=1000.0,
    )

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=thermal_model,
    )

    state = simulation.step(
        dt_s=10.0,
        heat_removed_mw=2000.0,
    )

    assert state.temperature_k < 573.15

def test_full_cycle_net_power_is_lower_than_gross_power():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
        power_cycle=create_power_cycle(),
    )

    state = simulation.step(
        dt_s=0.0,
        heat_removed_mw=0.0,
    )

    assert state.electrical_power_mw > 0.0
    assert state.net_electrical_power_mw <= (
        state.electrical_power_mw
    )

def test_scram_removes_electrical_generation():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
        power_cycle=create_power_cycle(),
    )

    reactor.scram()

    state = simulation.step(
        dt_s=0.0,
        heat_removed_mw=0.0,
    )

    assert state.power_mw == pytest.approx(0.0)
    assert state.electrical_power_mw == pytest.approx(0.0)
    assert state.net_electrical_power_mw == pytest.approx(0.0)
    assert state.reactor_status == "shutdown"

def test_external_reactivity_is_propagated_through_plant_simulation():
    reactor = Reactor(rated_power_mw=3000)

    dynamics = ReactorDynamics(
        rated_power_mw=3000,
        initial_power_fraction=1.0,
    )

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
        reactor_dynamics=dynamics,
    )

    state = simulation.step(
        dt_s=0.1,
        heat_removed_mw=3000.0,
        external_reactivity=0.0001,
    )

    assert state.external_reactivity == pytest.approx(
        0.0001
    )
    assert state.total_reactivity > 0.0
    assert state.power_mw > 0.0

def test_plant_simulation_updates_instrumentation():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    instrumentation = PlantInstrumentation()

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
        power_cycle=create_power_cycle(),
        instrumentation=instrumentation,
    )

    state = simulation.step(
        dt_s=0.0,
        heat_removed_mw=0.0,
    )

    power_sensor = instrumentation.system.get_sensor(
        "reactor_power"
    ).read()

    assert power_sensor.value == pytest.approx(
        state.power_mw
    )

def test_plant_simulation_instrumentation_uses_state_timestamp():
    reactor = Reactor(rated_power_mw=3000)
    instrumentation = PlantInstrumentation()

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
        instrumentation=instrumentation,
    )

    state = simulation.step(
        dt_s=10.0,
        heat_removed_mw=0.0,
    )

    temperature_sensor = instrumentation.system.get_sensor(
        "reactor_temperature"
    ).read()

    assert temperature_sensor.timestamp_s == pytest.approx(
        state.time_s
    )

def test_plant_simulation_accepts_controller():
    from nuclear_sim.plant.plant_controller import PlantController

    reactor = Reactor(rated_power_mw=3000)
    thermal_model = ThermalModel()

    controller = PlantController(reactor)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=thermal_model,
        controller=controller,
    )

    assert simulation.controller is controller

def test_plant_simulation_controls_reactor_power():
    from nuclear_sim.plant.plant_controller import PlantController

    reactor = Reactor(rated_power_mw=3000)
    thermal_model = ThermalModel()
    controller = PlantController(reactor)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=thermal_model,
        controller=controller,
    )

    simulation.set_reactor_power(0.5)

    assert reactor.state().power_mw == pytest.approx(1500.0)
    assert controller.power_control.state().position == pytest.approx(0.5)

def test_plant_simulation_controls_scram():
    from nuclear_sim.plant.plant_controller import PlantController

    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    thermal_model = ThermalModel()
    controller = PlantController(reactor)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=thermal_model,
        controller=controller,
    )

    simulation.scram()

    assert reactor.state().power_mw == pytest.approx(0.0)
    assert controller.scram_actuator.state().position == pytest.approx(1.0)

def test_plant_simulation_rejects_control_without_controller():
    reactor = Reactor(rated_power_mw=3000)
    thermal_model = ThermalModel()

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=thermal_model,
    )

    with pytest.raises(RuntimeError):
        simulation.set_reactor_power(0.5)

    with pytest.raises(RuntimeError):
        simulation.scram()

def test_controller_updates_instrumentation_after_simulation_step():
    from nuclear_sim.plant.plant_controller import PlantController
    from nuclear_sim.plant.plant_instrumentation import PlantInstrumentation

    reactor = Reactor(rated_power_mw=3000)
    thermal_model = ThermalModel()
    instrumentation = PlantInstrumentation()
    controller = PlantController(
        reactor=reactor,
        instrumentation=instrumentation,
    )

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=thermal_model,
        instrumentation=instrumentation,
        controller=controller,
    )

    simulation.set_reactor_power(0.5)

    state = simulation.step(
        dt_s=1.0,
        heat_removed_mw=0.0,
    )

    sensor = instrumentation.system.get_sensor("reactor_power")

    assert state.power_mw == pytest.approx(1500.0)
    assert sensor.read().value == pytest.approx(1500.0)
    assert sensor.read().timestamp_s == pytest.approx(1.0)

def test_controller_scram_updates_instrumentation_after_simulation_step():
    from nuclear_sim.plant.plant_controller import PlantController
    from nuclear_sim.plant.plant_instrumentation import PlantInstrumentation

    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    thermal_model = ThermalModel()
    instrumentation = PlantInstrumentation()

    controller = PlantController(
        reactor=reactor,
        instrumentation=instrumentation,
    )

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=thermal_model,
        instrumentation=instrumentation,
        controller=controller,
    )

    simulation.scram()

    state = simulation.step(
        dt_s=1.0,
        heat_removed_mw=0.0,
    )

    scram_actuator = instrumentation.system.get_actuator("scram")
    power_sensor = instrumentation.system.get_sensor("reactor_power")

    assert state.power_mw == pytest.approx(0.0)
    assert scram_actuator.state().position == pytest.approx(1.0)
    assert power_sensor.read().value == pytest.approx(0.0)
    assert power_sensor.read().timestamp_s == pytest.approx(1.0)

def test_controller_updates_dynamic_reactivity_during_step():
    reactor = Reactor(rated_power_mw=3000)
    dynamics = ReactorDynamics(rated_power_mw=3000)

    controller = PlantController(
        reactor=reactor,
        reactor_dynamics=dynamics,
        control_gain=0.02,
    )

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
        reactor_dynamics=dynamics,
        controller=controller,
    )

    simulation.set_reactor_power(0.8)

    initial_fraction = (
        dynamics.state().power_mw
        / reactor.rated_power_mw
    )

    expected_reactivity = (
        0.02 * (0.8 - initial_fraction)
    )

    expected_reactivity = max(
        -0.002,
        min(expected_reactivity, 0.002),
    )

    simulation.step(
        dt_s=0.1,
        heat_removed_mw=0.0,
    )

    assert dynamics.control_reactivity() == pytest.approx(
        expected_reactivity
    )

def test_dynamic_controller_reacts_to_power_changes():
    reactor = Reactor(rated_power_mw=3000)
    dynamics = ReactorDynamics(rated_power_mw=3000)

    controller = PlantController(
        reactor=reactor,
        reactor_dynamics=dynamics,
        control_gain=0.02,
    )

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
        reactor_dynamics=dynamics,
        controller=controller,
    )

    simulation.set_reactor_power(0.8)

    initial_power = dynamics.state().power_mw
    reactivities = []

    for _ in range(5):
        state = simulation.step(
            dt_s=0.1,
            heat_removed_mw=0.0,
        )
        reactivities.append(
            dynamics.control_reactivity()
        )

    assert state.power_mw != pytest.approx(
        initial_power
    )

    assert len(set(reactivities)) > 1

def test_dynamic_controller_converges_towards_target_power():
    reactor = Reactor(rated_power_mw=3000)
    dynamics = ReactorDynamics(rated_power_mw=3000)

    controller = PlantController(
        reactor=reactor,
        reactor_dynamics=dynamics,
        control_gain=0.006,
    )

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
        reactor_dynamics=dynamics,
        controller=controller,
    )

    simulation.set_reactor_power(0.8)

    initial_error = abs(
        0.8
        - (
            dynamics.state().power_mw
            / reactor.rated_power_mw
        )
    )

    for _ in range(20):
        state = simulation.step(
            dt_s=0.1,
            heat_removed_mw=0.0,
        )

    final_fraction = (
        state.power_mw
        / reactor.rated_power_mw
    )

    final_error = abs(
        0.8 - final_fraction
    )

    assert final_error < initial_error

def test_dynamic_controller_stabilizes_near_target_power():
    reactor = Reactor(rated_power_mw=3000)
    dynamics = ReactorDynamics(rated_power_mw=3000)

    controller = PlantController(
        reactor=reactor,
        reactor_dynamics=dynamics,
        control_gain=0.006,
    )

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
        reactor_dynamics=dynamics,
        controller=controller,
    )

    simulation.set_reactor_power(0.8)

    for _ in range(100):
        state = simulation.step(
            dt_s=0.1,
            heat_removed_mw=0.0,
        )

    final_fraction = (
        state.power_mw
        / reactor.rated_power_mw
    )

    assert final_fraction < 1.0
    assert final_fraction > 0.0

def test_dynamic_controller_power_evolution():
    reactor = Reactor(rated_power_mw=3000)
    dynamics = ReactorDynamics(rated_power_mw=3000)

    controller = PlantController(
        reactor=reactor,
        reactor_dynamics=dynamics,
        control_gain=0.01,
    )

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
        reactor_dynamics=dynamics,
        controller=controller,
    )

    simulation.set_reactor_power(0.8)

    for step in range(100):
        state = simulation.step(
            dt_s=0.1,
            heat_removed_mw=0.0,
        )

        power_fraction = (
            state.power_mw
            / reactor.rated_power_mw
        )

        if (step + 1) % 10 == 0:
            print(
                f"Paso {step + 1:03d}: "
                f"potencia={power_fraction:.6f}, "
                f"reactividad={dynamics.control_reactivity():.8f}"
            )

def test_plant_safety_integration_evaluates_primary_pressure():
    reactor = Reactor(rated_power_mw=3000)
    thermal_model = ThermalModel()
    power_cycle = create_power_cycle()

    safety = SafetySystem()

    safety.add_limit(
        SafetyLimit(
            name="Primary Pressure",
            warning=15.0,
            critical=16.0,
        )
    )

    safety.add_limit(
        SafetyLimit(
            name="Core Temperature",
            warning=700.0,
            critical=800.0,
        )
    )

    safety_integration = SafetyIntegration(
        reactor=reactor,
        safety_system=safety,
    )

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=thermal_model,
        power_cycle=power_cycle,
        safety_integration=safety_integration,
    )

    simulation.step(
        dt_s=1.0,
        heat_removed_mw=0.0,
    )


    assert simulation._safety_state is not None
    assert simulation._safety_state.assessment.overall_status == "warning"
    assert len(simulation._safety_state.incidents) == 1
    assert simulation._safety_state.incidents[0].name == "Primary Pressure"