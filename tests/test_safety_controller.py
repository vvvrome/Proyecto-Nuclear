import pytest

from nuclear_sim.plant.reactor import Reactor
from nuclear_sim.safety.controller import SafetyController
from nuclear_sim.safety.limits import SafetyLimit
from nuclear_sim.safety.system import SafetyAssessment


def test_critical_assessment_triggers_scram():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    controller = SafetyController(reactor)

    assessment = SafetyAssessment(
        overall_status="critical",
        results={"Core Temperature": "critical"},
    )

    controller.apply(assessment)

    assert reactor.state().power_mw == pytest.approx(0.0)
    assert reactor.state().status == "shutdown"


def test_normal_assessment_does_not_scram():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(1.0)

    controller = SafetyController(reactor)

    assessment = SafetyAssessment(
        overall_status="normal",
        results={"Core Temperature": "normal"},
    )

    controller.apply(assessment)

    assert reactor.state().power_mw == pytest.approx(3000.0)
    assert reactor.state().status == "full_power"


def test_warning_assessment_does_not_scram():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(0.5)

    controller = SafetyController(reactor)

    assessment = SafetyAssessment(
        overall_status="warning",
        results={"Core Temperature": "warning"},
    )

    controller.apply(assessment)

    assert reactor.state().power_mw == pytest.approx(1500.0)
    assert reactor.state().status == "operating"


def test_critical_assessment_scrams_from_partial_power():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(0.65)

    controller = SafetyController(reactor)

    assessment = SafetyAssessment(
        overall_status="critical",
        results={"Core Temperature": "critical"},
    )

    controller.apply(assessment)

    assert reactor.state().power_mw == pytest.approx(0.0)
    assert reactor.state().status == "shutdown"


def test_normal_assessment_preserves_reactor_state():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(0.25)

    controller = SafetyController(reactor)

    assessment = SafetyAssessment(
        overall_status="normal",
        results={"Core Temperature": "normal"},
    )

    controller.apply(assessment)

    assert reactor.state().power_mw == pytest.approx(750.0)
    assert reactor.state().status == "operating"


def test_critical_assessment_with_multiple_results_triggers_scram():
    reactor = Reactor(rated_power_mw=3000)
    reactor.set_power_fraction(0.8)

    controller = SafetyController(reactor)

    assessment = SafetyAssessment(
        overall_status="critical",
        results={
            "Core Temperature": "warning",
            "Primary Pressure": "critical",
            "Radiation": "normal",
        },
    )

    controller.apply(assessment)

    assert reactor.state().power_mw == pytest.approx(0.0)
    assert reactor.state().status == "shutdown"