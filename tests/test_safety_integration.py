import pytest

from nuclear_sim.plant.reactor import Reactor
from nuclear_sim.plant.safety_integration import SafetyIntegration
from nuclear_sim.safety.limits import SafetyLimit
from nuclear_sim.safety.system import SafetySystem
from nuclear_sim.safety.incident import Incident

def create_integration():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    safety = SafetySystem()

    safety.add_limit(
        SafetyLimit(
            name="Core Temperature",
            warning=700.0,
            critical=800.0,
        )
    )

    safety.add_limit(
        SafetyLimit(
            name="Primary Pressure",
            warning=150.0,
            critical=200.0,
        )
    )

    return reactor, SafetyIntegration(reactor, safety)


def test_normal_condition_generates_no_alarms():
    reactor, integration = create_integration()

    state = integration.evaluate(
        {
            "Core Temperature": 650.0,
            "Primary Pressure": 100.0,
        }
    )

    assert state.assessment.overall_status == "normal"
    assert state.alarms == ()
    assert state.emergency_active is False
    assert reactor.state().power_mw == pytest.approx(3000.0)


def test_warning_condition_generates_warning_alarm():
    reactor, integration = create_integration()

    state = integration.evaluate(
        {
            "Core Temperature": 750.0,
            "Primary Pressure": 100.0,
        }
    )

    assert state.assessment.overall_status == "warning"
    assert len(state.alarms) == 1
    assert state.alarms[0].severity == "warning"
    assert state.emergency_active is False
    assert reactor.state().power_mw == pytest.approx(3000.0)


def test_critical_condition_generates_critical_alarm():
    reactor, integration = create_integration()

    state = integration.evaluate(
        {
            "Core Temperature": 850.0,
            "Primary Pressure": 100.0,
        }
    )

    assert state.assessment.overall_status == "critical"
    assert len(state.alarms) == 1
    assert state.alarms[0].severity == "critical"
    assert state.emergency_active is True
    assert reactor.state().power_mw == pytest.approx(0.0)


def test_multiple_conditions_generate_multiple_alarms():
    reactor, integration = create_integration()

    state = integration.evaluate(
        {
            "Core Temperature": 850.0,
            "Primary Pressure": 180.0,
        }
    )

    assert state.assessment.overall_status == "critical"
    assert len(state.alarms) == 2
    assert state.emergency_active is True
    assert reactor.state().power_mw == pytest.approx(0.0)


def test_warning_and_critical_prioritize_critical():
    reactor, integration = create_integration()

    state = integration.evaluate(
        {
            "Core Temperature": 750.0,
            "Primary Pressure": 250.0,
        }
    )

    assert state.assessment.overall_status == "critical"
    assert len(state.alarms) == 2
    assert state.emergency_active is True
    assert reactor.state().status == "shutdown"

def test_warning_condition_creates_incident():
    reactor, integration = create_integration()

    state = integration.evaluate(
        {
            "Core Temperature": 750.0,
            "Primary Pressure": 100.0,
        }
    )

    assert len(state.incidents) == 1

    incident = state.incidents[0]

    assert incident.name == "Core Temperature"
    assert incident.severity == "warning"
    assert incident.status == "open"


def test_repeated_condition_does_not_create_duplicate_incident():
    reactor, integration = create_integration()

    first_state = integration.evaluate(
        {
            "Core Temperature": 750.0,
            "Primary Pressure": 100.0,
        }
    )

    second_state = integration.evaluate(
        {
            "Core Temperature": 750.0,
            "Primary Pressure": 100.0,
        }
    )

    assert len(first_state.incidents) == 1
    assert len(second_state.incidents) == 1

    assert (
        first_state.incidents[0].name
        == second_state.incidents[0].name
    )


def test_incident_is_resolved_when_condition_returns_to_normal():
    reactor, integration = create_integration()

    integration.evaluate(
        {
            "Core Temperature": 750.0,
            "Primary Pressure": 100.0,
        }
    )

    state = integration.evaluate(
        {
            "Core Temperature": 650.0,
            "Primary Pressure": 100.0,
        }
    )

    assert len(state.incidents) == 1
    assert state.incidents[0].name == "Core Temperature"
    assert state.incidents[0].status == "resolved"

def test_repeated_condition_reuses_active_incident():
    reactor, integration = create_integration()

    first_state = integration.evaluate(
        {
            "Core Temperature": 750.0,
            "Primary Pressure": 100.0,
        },
        timestamp_s=1.0,
    )

    second_state = integration.evaluate(
        {
            "Core Temperature": 750.0,
            "Primary Pressure": 100.0,
        },
        timestamp_s=2.0,
    )

    first_incident = first_state.incidents[0]
    second_incident = second_state.incidents[0]

    assert first_incident.name == second_incident.name
    assert first_incident.timestamp_s == pytest.approx(1.0)
    assert second_incident.timestamp_s == pytest.approx(1.0)
    assert first_incident.status == "open"
    assert second_incident.status == "open"