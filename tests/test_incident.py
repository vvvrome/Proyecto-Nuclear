import pytest

from nuclear_sim.safety.incident import Incident


def test_incident_creation():
    incident = Incident(
        timestamp_s=12.5,
        name="Core Temperature",
        severity="warning",
        message="Temperature above warning limit.",
        source="SafetySystem",
    )

    assert incident.timestamp_s == pytest.approx(12.5)
    assert incident.name == "Core Temperature"
    assert incident.severity == "warning"
    assert incident.message == "Temperature above warning limit."
    assert incident.source == "SafetySystem"
    assert incident.status == "open"


def test_incident_can_be_resolved():
    incident = Incident(
        timestamp_s=20.0,
        name="Primary Pressure",
        severity="critical",
        message="Critical pressure detected.",
        source="SafetySystem",
        status="resolved",
    )

    assert incident.status == "resolved"


def test_incident_is_immutable():
    incident = Incident(
        timestamp_s=10.0,
        name="Temperature",
        severity="warning",
        message="High temperature.",
        source="SafetySystem",
    )

    with pytest.raises(AttributeError):
        incident.status = "resolved"


def test_empty_name_is_rejected():
    with pytest.raises(ValueError):
        Incident(
            timestamp_s=10.0,
            name="",
            severity="warning",
            message="Test",
            source="SafetySystem",
        )


def test_invalid_severity_is_rejected():
    with pytest.raises(ValueError):
        Incident(
            timestamp_s=10.0,
            name="Temperature",
            severity="info",
            message="Test",
            source="SafetySystem",
        )


def test_invalid_status_is_rejected():
    with pytest.raises(ValueError):
        Incident(
            timestamp_s=10.0,
            name="Temperature",
            severity="warning",
            message="Test",
            source="SafetySystem",
            status="invalid",
        )


def test_negative_timestamp_is_rejected():
    with pytest.raises(ValueError):
        Incident(
            timestamp_s=-1.0,
            name="Temperature",
            severity="warning",
            message="Test",
            source="SafetySystem",
        )