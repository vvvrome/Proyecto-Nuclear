import pytest

from nuclear_sim.safety.alarm import Alarm


def test_alarm_creation():
    alarm = Alarm(
        name="Core Temperature",
        severity="warning",
        message="Temperature above warning limit.",
    )

    assert alarm.name == "Core Temperature"
    assert alarm.severity == "warning"
    assert alarm.message == "Temperature above warning limit."
    assert alarm.active is True


def test_alarm_can_be_inactive():
    alarm = Alarm(
        name="Radiation",
        severity="critical",
        message="Critical radiation level.",
        active=False,
    )

    assert alarm.active is False


def test_empty_name_is_rejected():
    with pytest.raises(ValueError):
        Alarm(
            name="",
            severity="warning",
            message="Test",
        )


def test_invalid_severity_is_rejected():
    with pytest.raises(ValueError):
        Alarm(
            name="Temperature",
            severity="info",
            message="Test",
        )


def test_empty_message_is_rejected():
    with pytest.raises(ValueError):
        Alarm(
            name="Temperature",
            severity="warning",
            message="",
        )