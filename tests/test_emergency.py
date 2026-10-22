import pytest

from nuclear_sim.plant.reactor import Reactor
from nuclear_sim.safety.emergency import EmergencySystem


def test_emergency_system_starts_inactive():
    reactor = Reactor(rated_power_mw=3000)
    emergency = EmergencySystem(reactor)

    state = emergency.state()

    assert state.active is False
    assert state.cooling_active is False


def test_activate_emergency_scrams_reactor():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    emergency = EmergencySystem(reactor)

    state = emergency.activate()

    assert state.active is True
    assert state.cooling_active is True
    assert state.reactor_scrammed is True
    assert reactor.state().power_mw == pytest.approx(0.0)


def test_deactivate_emergency():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    emergency = EmergencySystem(reactor)
    emergency.activate()

    state = emergency.deactivate()

    assert state.active is False
    assert state.cooling_active is False
    assert state.reactor_scrammed is True


def test_activation_from_partial_power_scrams():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(0.4)

    emergency = EmergencySystem(reactor)
    emergency.activate()

    assert reactor.state().power_mw == pytest.approx(0.0)