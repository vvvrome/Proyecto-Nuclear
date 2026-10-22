import pytest

from nuclear_sim.safety.limits import SafetyLimit
from nuclear_sim.safety.system import SafetySystem


def test_safety_system_starts_empty():
    system = SafetySystem()

    assert system.limit_count() == 0


def test_add_safety_limit():
    system = SafetySystem()

    limit = SafetyLimit(
        name="Core Temperature",
        warning=650.0,
        critical=700.0,
    )

    system.add_limit(limit)

    assert system.limit_count() == 1


def test_normal_assessment():
    system = SafetySystem()

    system.add_limit(
        SafetyLimit(
            name="Core Temperature",
            warning=650.0,
            critical=700.0,
        )
    )

    assessment = system.evaluate(
        {"Core Temperature": 600.0}
    )

    assert assessment.overall_status == "normal"
    assert assessment.results["Core Temperature"] == "normal"


def test_warning_assessment():
    system = SafetySystem()

    system.add_limit(
        SafetyLimit(
            name="Core Temperature",
            warning=650.0,
            critical=700.0,
        )
    )

    assessment = system.evaluate(
        {"Core Temperature": 675.0}
    )

    assert assessment.overall_status == "warning"
    assert assessment.results["Core Temperature"] == "warning"


def test_critical_assessment():
    system = SafetySystem()

    system.add_limit(
        SafetyLimit(
            name="Core Temperature",
            warning=650.0,
            critical=700.0,
        )
    )

    assessment = system.evaluate(
        {"Core Temperature": 750.0}
    )

    assert assessment.overall_status == "critical"
    assert assessment.results["Core Temperature"] == "critical"


def test_critical_has_priority_over_warning():
    system = SafetySystem()

    system.add_limit(
        SafetyLimit(
            name="Core Temperature",
            warning=650.0,
            critical=700.0,
        )
    )

    system.add_limit(
        SafetyLimit(
            name="Primary Pressure",
            warning=100.0,
            critical=150.0,
        )
    )

    assessment = system.evaluate(
        {
            "Core Temperature": 675.0,
            "Primary Pressure": 160.0,
        }
    )

    assert assessment.overall_status == "critical"
    assert assessment.results["Core Temperature"] == "warning"
    assert assessment.results["Primary Pressure"] == "critical"


def test_multiple_normal_values():
    system = SafetySystem()

    system.add_limit(
        SafetyLimit(
            name="Core Temperature",
            warning=650.0,
            critical=700.0,
        )
    )

    system.add_limit(
        SafetyLimit(
            name="Primary Pressure",
            warning=100.0,
            critical=150.0,
        )
    )

    assessment = system.evaluate(
        {
            "Core Temperature": 600.0,
            "Primary Pressure": 80.0,
        }
    )

    assert assessment.overall_status == "normal"


def test_duplicate_limit_is_rejected():
    system = SafetySystem()

    system.add_limit(
        SafetyLimit(
            name="Core Temperature",
            warning=650.0,
            critical=700.0,
        )
    )

    with pytest.raises(ValueError):
        system.add_limit(
            SafetyLimit(
                name="Core Temperature",
                warning=600.0,
                critical=750.0,
            )
        )


def test_missing_value_is_rejected():
    system = SafetySystem()

    system.add_limit(
        SafetyLimit(
            name="Core Temperature",
            warning=650.0,
            critical=700.0,
        )
    )

    with pytest.raises(KeyError):
        system.evaluate({})


def test_assessment_contains_all_results():
    system = SafetySystem()

    system.add_limit(
        SafetyLimit(
            name="Core Temperature",
            warning=650.0,
            critical=700.0,
        )
    )

    system.add_limit(
        SafetyLimit(
            name="Primary Pressure",
            warning=100.0,
            critical=150.0,
        )
    )

    assessment = system.evaluate(
        {
            "Core Temperature": 600.0,
            "Primary Pressure": 120.0,
        }
    )

    assert len(assessment.results) == 2
    assert assessment.results["Core Temperature"] == "normal"
    assert assessment.results["Primary Pressure"] == "warning"