import math

import pytest

from nuclear_sim.nuclear.kinetics.temperature_feedback import (
    TemperatureFeedback,
)
from nuclear_sim.plant.reactor_dynamics import ReactorDynamics
from nuclear_sim.plant.reactor_kinetics import ReactorKinetics
from nuclear_sim.thermal.thermal_model import ThermalModel



def test_initial_state_is_at_reference_temperature():
    dynamics = ReactorDynamics(rated_power_mw=100.0)

    state = dynamics.state()

    assert state.time_s == 0.0
    assert state.power_mw == pytest.approx(100.0)
    assert state.power_fraction == pytest.approx(1.0)
    assert state.temperature_reactivity == pytest.approx(0.0)
    assert state.total_reactivity == pytest.approx(0.0)


def test_initial_precursors_are_in_equilibrium():
    dynamics = ReactorDynamics(rated_power_mw=100.0)

    state = dynamics.state()

    expected = (
        dynamics.reactor_kinetics.point_kinetics
        .equilibrium_precursor_population(
            state.neutron_population
        )
    )

    assert state.precursor_population == pytest.approx(expected)


def test_external_reactivity_is_stored():
    dynamics = ReactorDynamics(rated_power_mw=100.0)

    dynamics.set_external_reactivity(0.001)

    assert dynamics.external_reactivity == pytest.approx(0.001)


def test_external_reactivity_changes_total_reactivity():
    dynamics = ReactorDynamics(rated_power_mw=100.0)

    dynamics.set_external_reactivity(0.001)

    state = dynamics.state()

    assert state.external_reactivity == pytest.approx(0.001)
    assert state.temperature_reactivity == pytest.approx(0.0)
    assert state.total_reactivity == pytest.approx(0.001)


def test_temperature_feedback_is_included_in_total_reactivity():
    feedback = TemperatureFeedback(
        reference_temperature_k=573.15,
        temperature_coefficient_per_k=-1.0e-5,
    )

    thermal = ThermalModel(
        initial_temperature_k=583.15,
    )

    dynamics = ReactorDynamics(
        rated_power_mw=100.0,
        thermal_model=thermal,
        temperature_feedback=feedback,
    )

    state = dynamics.state()

    assert state.temperature_reactivity == pytest.approx(-1.0e-4)
    assert state.total_reactivity == pytest.approx(-1.0e-4)


def test_external_and_temperature_reactivity_are_combined():
    feedback = TemperatureFeedback(
        reference_temperature_k=573.15,
        temperature_coefficient_per_k=-1.0e-5,
    )

    thermal = ThermalModel(
        initial_temperature_k=583.15,
    )

    dynamics = ReactorDynamics(
        rated_power_mw=100.0,
        thermal_model=thermal,
        temperature_feedback=feedback,
    )

    dynamics.set_external_reactivity(0.001)

    state = dynamics.state()

    assert state.temperature_reactivity == pytest.approx(-1.0e-4)
    assert state.total_reactivity == pytest.approx(0.0009)


def test_step_advances_time():
    dynamics = ReactorDynamics(rated_power_mw=100.0)

    state = dynamics.step(
        dt_s=0.001,
        heat_removed_mw=100.0,
    )

    assert state.time_s == pytest.approx(0.001)


def test_step_with_balanced_heat_keeps_temperature_constant():
    dynamics = ReactorDynamics(rated_power_mw=100.0)

    initial_temperature = dynamics.temperature_k

    state = dynamics.step(
        dt_s=0.01,
        heat_removed_mw=100.0,
    )

    assert state.temperature_k == pytest.approx(
        initial_temperature
    )


def test_zero_time_step_does_not_change_state():
    dynamics = ReactorDynamics(rated_power_mw=100.0)

    initial = dynamics.state()

    state = dynamics.step(
        dt_s=0.0,
        heat_removed_mw=100.0,
    )

    assert state == initial


def test_positive_reactivity_changes_neutron_population():
    dynamics = ReactorDynamics(rated_power_mw=100.0)

    initial_population = dynamics.state().neutron_population

    state = dynamics.step(
        dt_s=0.001,
        heat_removed_mw=100.0,
        external_reactivity=0.001,
    )

    assert state.neutron_population > initial_population
    assert state.power_mw > 100.0


def test_negative_reactivity_reduces_neutron_population():
    dynamics = ReactorDynamics(rated_power_mw=100.0)

    initial_population = dynamics.state().neutron_population

    state = dynamics.step(
        dt_s=0.001,
        heat_removed_mw=100.0,
        external_reactivity=-0.001,
    )

    assert state.neutron_population < initial_population
    assert state.power_mw < 100.0


def test_temperature_rise_produces_negative_feedback():
    dynamics = ReactorDynamics(rated_power_mw=100.0)

    initial = dynamics.state()

    state = dynamics.step(
        dt_s=0.01,
        heat_removed_mw=0.0,
    )

    assert state.temperature_k > initial.temperature_k
    assert state.temperature_reactivity < 0.0


def test_invalid_inputs_are_rejected():
    dynamics = ReactorDynamics(rated_power_mw=100.0)

    with pytest.raises(ValueError):
        dynamics.step(
            dt_s=-1.0,
            heat_removed_mw=100.0,
        )

    with pytest.raises(ValueError):
        dynamics.step(
            dt_s=1.0,
            heat_removed_mw=-1.0,
        )

    with pytest.raises(ValueError):
        dynamics.set_external_reactivity(math.nan)

def test_control_reactivity_is_inittialy_zero():
    dynamics = ReactorDynamics(rated_power_mw=100.0)

    assert dynamics.control_reactivity() == pytest.approx(0.0)

def test_control_reactivity_can_be_set():
    dynamics = ReactorDynamics(rated_power_mw=3000)
    dynamics.set_control_reactivity(0.001)

    assert dynamics.control_reactivity() == pytest.approx(0.001)

def test_control_reactivity_affects_total_reactivity():
    dynamics = ReactorDynamics(rated_power_mw=3000)

    dynamics.set_control_reactivity(0.001)

    state = dynamics.step(
        dt_s=0.0,
        heat_removed_mw=3000.0,
    )

    assert state.total_reactivity == pytest.approx(0.001)

def test_positive_reactivity_increases_power():
    feedback = TemperatureFeedback(
        reference_temperature_k=573.15,
        temperature_coefficient_per_k=0.0,
    )

    kinetics = ReactorKinetics(
        rated_power_mw=3000,
        initial_power_fraction=0.5,
    )

    dynamics = ReactorDynamics(
        rated_power_mw=3000,
        reactor_kinetics=kinetics,
        temperature_feedback=feedback,
    )

    dynamics.set_control_reactivity(0.01)

    print("CONTROL:", dynamics.control_reactivity())
    print("TOTAL:", dynamics.state().total_reactivity)

    initial_power = dynamics.state().power_mw

    for _ in range(100):
        state = dynamics.step(
            dt_s=0.001,
            heat_removed_mw=0.0,
        )

    state = dynamics.step(
    dt_s=0.001,
    heat_removed_mw=0.0,
)

    print("NEUTRONES:", state.neutron_population)
    print("POTENCIA:", state.power_mw)
    print("REACTIVIDAD:", state.total_reactivity)

    assert state.power_mw > initial_power