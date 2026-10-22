import pytest

from nuclear_sim.instrumentation.sensor import Sensor


def test_sensor_initial_reading():
    sensor = Sensor(
        name="Core Temperature",
        unit="K",
        initial_value=573.15,
    )

    reading = sensor.read()

    assert reading.name == "Core Temperature"
    assert reading.value == pytest.approx(573.15)
    assert reading.unit == "K"
    assert reading.timestamp_s == pytest.approx(0.0)
    assert reading.status == "normal"


def test_sensor_update():
    sensor = Sensor(
        name="Core Temperature",
        unit="K",
    )

    reading = sensor.update(
        value=650.0,
        timestamp_s=10.0,
    )

    assert reading.value == pytest.approx(650.0)
    assert reading.timestamp_s == pytest.approx(10.0)


def test_sensor_update_persists_value():
    sensor = Sensor(
        name="Pressure",
        unit="bar",
    )

    sensor.update(
        value=155.0,
        timestamp_s=5.0,
    )

    reading = sensor.read()

    assert reading.value == pytest.approx(155.0)
    assert reading.timestamp_s == pytest.approx(5.0)


def test_sensor_status_can_be_changed():
    sensor = Sensor(
        name="Core Temperature",
        unit="K",
    )

    sensor.set_status("warning")

    assert sensor.read().status == "warning"


def test_sensor_rejects_empty_name():
    with pytest.raises(ValueError):
        Sensor(
            name="",
            unit="K",
        )


def test_sensor_rejects_empty_unit():
    with pytest.raises(ValueError):
        Sensor(
            name="Temperature",
            unit="",
        )


def test_sensor_rejects_non_finite_initial_value():
    with pytest.raises(ValueError):
        Sensor(
            name="Temperature",
            unit="K",
            initial_value=float("nan"),
        )


def test_sensor_rejects_non_finite_update():
    sensor = Sensor(
        name="Temperature",
        unit="K",
    )

    with pytest.raises(ValueError):
        sensor.update(
            value=float("inf"),
            timestamp_s=1.0,
        )


def test_sensor_rejects_negative_timestamp():
    sensor = Sensor(
        name="Temperature",
        unit="K",
    )

    with pytest.raises(ValueError):
        sensor.update(
            value=600.0,
            timestamp_s=-1.0,
        )


def test_sensor_rejects_non_finite_timestamp():
    sensor = Sensor(
        name="Temperature",
        unit="K",
    )

    with pytest.raises(ValueError):
        sensor.update(
            value=600.0,
            timestamp_s=float("nan"),
        )


def test_sensor_status_cannot_be_empty():
    sensor = Sensor(
        name="Temperature",
        unit="K",
    )

    with pytest.raises(ValueError):
        sensor.set_status("")