import pytest

from nuclear_sim.instrumentation.actuator import Actuator
from nuclear_sim.instrumentation.sensor import Sensor
from nuclear_sim.instrumentation.system import InstrumentationSystem


def test_instrumentation_system_starts_empty():
    system = InstrumentationSystem()

    assert system.sensor_count() == 0
    assert system.actuator_count() == 0


def test_add_sensor():
    system = InstrumentationSystem()
    sensor = Sensor(
        name="Core Temperature",
        unit="K",
    )

    system.add_sensor(sensor)

    assert system.sensor_count() == 1


def test_get_sensor():
    system = InstrumentationSystem()
    sensor = Sensor(
        name="Core Temperature",
        unit="K",
    )

    system.add_sensor(sensor)

    result = system.get_sensor("Core Temperature")

    assert result is sensor


def test_add_multiple_sensors():
    system = InstrumentationSystem()

    system.add_sensor(
        Sensor(
            name="Core Temperature",
            unit="K",
        )
    )

    system.add_sensor(
        Sensor(
            name="Primary Pressure",
            unit="bar",
        )
    )

    assert system.sensor_count() == 2


def test_duplicate_sensor_is_rejected():
    system = InstrumentationSystem()

    system.add_sensor(
        Sensor(
            name="Core Temperature",
            unit="K",
        )
    )

    with pytest.raises(ValueError):
        system.add_sensor(
            Sensor(
                name="Core Temperature",
                unit="K",
            )
        )


def test_add_actuator():
    system = InstrumentationSystem()
    actuator = Actuator(
        name="Cooling Valve",
    )

    system.add_actuator(actuator)

    assert system.actuator_count() == 1


def test_get_actuator():
    system = InstrumentationSystem()
    actuator = Actuator(
        name="Cooling Valve",
    )

    system.add_actuator(actuator)

    result = system.get_actuator("Cooling Valve")

    assert result is actuator


def test_add_multiple_actuators():
    system = InstrumentationSystem()

    system.add_actuator(
        Actuator(
            name="Cooling Valve",
        )
    )

    system.add_actuator(
        Actuator(
            name="Feedwater Pump",
        )
    )

    assert system.actuator_count() == 2


def test_duplicate_actuator_is_rejected():
    system = InstrumentationSystem()

    system.add_actuator(
        Actuator(
            name="Cooling Valve",
        )
    )

    with pytest.raises(ValueError):
        system.add_actuator(
            Actuator(
                name="Cooling Valve",
            )
        )


def test_missing_sensor_is_rejected():
    system = InstrumentationSystem()

    with pytest.raises(KeyError):
        system.get_sensor("Nonexistent Sensor")