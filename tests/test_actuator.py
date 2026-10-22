import pytest

from nuclear_sim.instrumentation.actuator import Actuator


def test_actuator_initial_state():
    actuator = Actuator(
        name="Control Rod",
        initial_position=0.0,
    )

    state = actuator.state()

    assert state.name == "Control Rod"
    assert state.position == pytest.approx(0.0)
    assert state.timestamp_s == pytest.approx(0.0)
    assert state.status == "ready"


def test_actuator_custom_initial_position():
    actuator = Actuator(
        name="Control Rod",
        initial_position=0.5,
    )

    assert actuator.state().position == pytest.approx(0.5)


def test_actuator_set_position():
    actuator = Actuator(
        name="Control Rod",
    )

    state = actuator.set_position(
        position=0.75,
        timestamp_s=10.0,
    )

    assert state.position == pytest.approx(0.75)
    assert state.timestamp_s == pytest.approx(10.0)


def test_actuator_position_persists():
    actuator = Actuator(
        name="Valve",
    )

    actuator.set_position(
        position=0.6,
        timestamp_s=5.0,
    )

    state = actuator.state()

    assert state.position == pytest.approx(0.6)
    assert state.timestamp_s == pytest.approx(5.0)


def test_actuator_status_can_be_changed():
    actuator = Actuator(
        name="Pump",
    )

    actuator.set_status("running")

    assert actuator.state().status == "running"


def test_actuator_rejects_empty_name():
    with pytest.raises(ValueError):
        Actuator(name="")


def test_actuator_rejects_invalid_initial_position():
    with pytest.raises(ValueError):
        Actuator(
            name="Valve",
            initial_position=1.5,
        )


def test_actuator_rejects_negative_position():
    actuator = Actuator(name="Valve")

    with pytest.raises(ValueError):
        actuator.set_position(
            position=-0.1,
            timestamp_s=1.0,
        )


def test_actuator_rejects_position_above_one():
    actuator = Actuator(name="Valve")

    with pytest.raises(ValueError):
        actuator.set_position(
            position=1.1,
            timestamp_s=1.0,
        )


def test_actuator_rejects_negative_timestamp():
    actuator = Actuator(name="Valve")

    with pytest.raises(ValueError):
        actuator.set_position(
            position=0.5,
            timestamp_s=-1.0,
        )


def test_actuator_status_cannot_be_empty():
    actuator = Actuator(name="Valve")

    with pytest.raises(ValueError):
        actuator.set_status("")