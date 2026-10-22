import pytest

from nuclear_sim.safety.limits import SafetyLimit


def test_safety_limit_normal():
    limit = SafetyLimit(
        name="Core Temperature",
        warning=650.0,
        critical=700.0,
    )

    assert limit.evaluate(600.0) == "normal"


def test_safety_limit_warning():
    limit = SafetyLimit(
        name="Core Temperature",
        warning=650.0,
        critical=700.0,
    )

    assert limit.evaluate(675.0) == "warning"


def test_safety_limit_critical():
    limit = SafetyLimit(
        name="Core Temperature",
        warning=650.0,
        critical=700.0,
    )

    assert limit.evaluate(750.0) == "critical"


def test_warning_threshold_is_warning():
    limit = SafetyLimit(
        name="Core Temperature",
        warning=650.0,
        critical=700.0,
    )

    assert limit.evaluate(650.0) == "warning"


def test_critical_threshold_is_critical():
    limit = SafetyLimit(
        name="Core Temperature",
        warning=650.0,
        critical=700.0,
    )

    assert limit.evaluate(700.0) == "critical"


def test_empty_name_is_rejected():
    with pytest.raises(ValueError):
        SafetyLimit(
            name="",
            warning=650.0,
            critical=700.0,
        )


def test_warning_greater_than_critical_is_rejected():
    with pytest.raises(ValueError):
        SafetyLimit(
            name="Core Temperature",
            warning=700.0,
            critical=650.0,
        )


def test_equal_warning_and_critical_is_rejected():
    with pytest.raises(ValueError):
        SafetyLimit(
            name="Core Temperature",
            warning=700.0,
            critical=700.0,
        )