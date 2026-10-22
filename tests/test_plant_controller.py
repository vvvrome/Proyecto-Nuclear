import pytest

from nuclear_sim.plant.reactor import Reactor
from nuclear_sim.plant.plant_controller import PlantController
from nuclear_sim.plant.simulation import PlantSimulation
from nuclear_sim.thermal.thermal_model import ThermalModel
from nuclear_sim.plant.reactor_dynamics import ReactorDynamics

def test_controller_starts_with_reactor_power():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(0.5)

    controller = PlantController(reactor)

    states = controller.actuator_states()

    assert states["reactor_power_control"].position == pytest.approx(0.5)
    assert states["scram"].position == pytest.approx(0.0)


def test_controller_changes_reactor_power():
    reactor = Reactor(rated_power_mw=3000)

    controller = PlantController(reactor)

    controller.set_reactor_power(
        power_fraction=0.5,
        timestamp_s=10.0,
    )

    assert reactor.state().power_mw == pytest.approx(1500.0)

    state = controller.actuator_states()["reactor_power_control"]

    assert state.position == pytest.approx(0.5)
    assert state.timestamp_s == pytest.approx(10.0)


def test_controller_scram_stops_reactor():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    controller = PlantController(reactor)

    controller.scram(timestamp_s=20.0)

    assert reactor.state().power_mw == pytest.approx(0.0)
    assert reactor.state().status == "shutdown"

    state = controller.actuator_states()["scram"]

    assert state.position == pytest.approx(1.0)
    assert state.timestamp_s == pytest.approx(20.0)


def test_controller_rejects_invalid_power():
    reactor = Reactor(rated_power_mw=3000)
    controller = PlantController(reactor)

    with pytest.raises(ValueError):
        controller.set_reactor_power(
            power_fraction=1.5,
            timestamp_s=0.0,
        )


def test_controller_rejects_negative_power():
    reactor = Reactor(rated_power_mw=3000)
    controller = PlantController(reactor)

    with pytest.raises(ValueError):
        controller.set_reactor_power(
            power_fraction=-0.1,
            timestamp_s=0.0,
        )

def test_controller_uses_instrumentation_actuators():
    from nuclear_sim.plant.plant_instrumentation import PlantInstrumentation

    reactor = Reactor(rated_power_mw=3000)
    instrumentation = PlantInstrumentation()

    controller = PlantController(
        reactor=reactor,
        instrumentation=instrumentation,
    )

    controller.set_reactor_power(
        power_fraction=0.5,
        timestamp_s=10.0,
    )

    actuator = instrumentation.system.get_actuator(
        "reactor_power_control"
    )

    assert actuator.state().position == pytest.approx(0.5)
    assert actuator.state().timestamp_s == pytest.approx(10.0)


def test_instrumentation_scram_actuator_is_updated_by_controller():
    from nuclear_sim.plant.plant_instrumentation import PlantInstrumentation

    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    instrumentation = PlantInstrumentation()

    controller = PlantController(
        reactor=reactor,
        instrumentation=instrumentation,
    )

    controller.scram(timestamp_s=20.0)

    actuator = instrumentation.system.get_actuator("scram")

    assert actuator.state().position == pytest.approx(1.0)
    assert actuator.state().timestamp_s == pytest.approx(20.0)
    assert reactor.state().power_mw == pytest.approx(0.0)

def test_controller_scram_updates_reactor_dynamics():
    from nuclear_sim.plant.reactor_dynamics import ReactorDynamics

    reactor = Reactor(rated_power_mw=3000)
    dynamics = ReactorDynamics(rated_power_mw=3000)

    controller = PlantController(
        reactor=reactor,
        reactor_dynamics=dynamics,
    )

    controller.scram(timestamp_s=10.0)

    state = dynamics.state()

    assert state.power_fraction == pytest.approx(0.0)
    assert state.neutron_population == pytest.approx(0.0)
    assert state.total_reactivity == pytest.approx(0.0)
    assert controller.scram_actuator.state().position == pytest.approx(1.0)

def test_plant_simulation_scram_controls_reactor_dynamics():
    from nuclear_sim.plant.plant_controller import PlantController
    from nuclear_sim.plant.reactor_dynamics import ReactorDynamics

    reactor = Reactor(rated_power_mw=3000)
    dynamics = ReactorDynamics(rated_power_mw=3000)
    thermal_model = ThermalModel()

    controller = PlantController(
        reactor=reactor,
        reactor_dynamics=dynamics,
    )

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=thermal_model,
        reactor_dynamics=dynamics,
        controller=controller,
    )

    simulation.scram()

    state = simulation.step(
        dt_s=1.0,
        heat_removed_mw=0.0,
    )

    assert state.power_mw == pytest.approx(0.0)
    assert state.reactor_status == "shutdown"
    assert dynamics.state().neutron_population == pytest.approx(0.0)
    assert controller.scram_actuator.state().position == pytest.approx(1.0)

def test_dynamic_controller_initializes_target_power():
    reactor = Reactor(rated_power_mw=3000)
    dynamics = ReactorDynamics(rated_power_mw=3000)

    controller = PlantController(
        reactor=reactor,
        reactor_dynamics=dynamics,
    )

    assert controller.target_power_fraction == pytest.approx(0.0)

def test_dynamic_controller_sets_target_power():
    reactor = Reactor(rated_power_mw=3000)
    dynamics = ReactorDynamics(rated_power_mw=3000)

    controller = PlantController(
        reactor=reactor,
        reactor_dynamics=dynamics,
    )

    controller.set_reactor_power(
        power_fraction=0.8,
        timestamp_s=0.0,
    )

    assert controller.target_power_fraction == pytest.approx(0.8)

def test_dynamic_controller_generates_control_reactivity():
    reactor = Reactor(rated_power_mw=3000)
    dynamics = ReactorDynamics(rated_power_mw=3000)

    controller = PlantController(
        reactor=reactor,
        reactor_dynamics=dynamics,
        control_gain=0.01,
    )

    controller.set_reactor_power(
        power_fraction=0.8,
        timestamp_s=0.0,
    )

    assert dynamics.control_reactivity() == pytest.approx(-0.002)

def test_dynamic_controller_updates_control_reactivity():
    reactor = Reactor(rated_power_mw=3000)
    dynamics = ReactorDynamics(rated_power_mw=3000)

    controller = PlantController(
        reactor=reactor,
        reactor_dynamics=dynamics,
        control_gain=0.01,
    )

    controller.set_reactor_power(
        power_fraction=0.8,
        timestamp_s=0.0,
    )

    dynamics.step(
        dt_s=0.1,
        heat_removed_mw=0.0,
    )

    control_reactivity = controller.update_control()

    current_fraction = (
        dynamics.state().power_mw
        / reactor.rated_power_mw
    )

    expected = (
        0.01
        * (0.8 - current_fraction)
    )

    assert control_reactivity == pytest.approx(expected)

def test_control_reactivity_is_limited():
    reactor = Reactor(rated_power_mw=3000)
    dynamics = ReactorDynamics(rated_power_mw=3000)

    controller = PlantController(
        reactor=reactor,
        reactor_dynamics=dynamics,
        control_gain=0.01,
        control_reactivity_limit=0.001,
    )

    controller.set_reactor_power(
        power_fraction=0.0,
        timestamp_s=0.0,
    )

    assert dynamics.control_reactivity() == pytest.approx(-0.001)

def test_positive_control_reactivity_is_limited():
    reactor = Reactor(rated_power_mw=3000)
    dynamics = ReactorDynamics(
        rated_power_mw=3000,
        initial_power_fraction=0.1,
    )

    controller = PlantController(
        reactor=reactor,
        reactor_dynamics=dynamics,
        control_gain=0.01,
        control_reactivity_limit=0.001,
    )

    controller.set_reactor_power(
        power_fraction=1.0,
        timestamp_s=0.0,
    )

    assert dynamics.control_reactivity() == pytest.approx(0.001)

def test_control_reactivity_limit_must_be_positive():
    reactor = Reactor(rated_power_mw=3000)

    with pytest.raises(ValueError):
        PlantController(
            reactor=reactor,
            control_reactivity_limit=0.0,
        )