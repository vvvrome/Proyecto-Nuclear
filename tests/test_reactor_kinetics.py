import pytest

from nuclear_sim.plant.reactor_kinetics import PointKinetics


def test_initial_state_is_critical_equilibrium():
    model = PointKinetics()
    state = model.state()

    assert state.time_s == pytest.approx(0.0)
    assert state.neutron_population == pytest.approx(1.0)
    assert state.normalized_power == pytest.approx(1.0)
    assert state.reactivity == pytest.approx(0.0)


def test_zero_reactivity_preserves_equilibrium():
    model = PointKinetics()
    state = model.advance(1.0)

    assert state.normalized_power == pytest.approx(1.0, rel=1e-6)


def test_positive_reactivity_increases_power():
    model = PointKinetics()
    model.set_reactivity(0.001)

    initial = model.state().normalized_power
    final = model.advance(0.05).normalized_power

    assert final > initial


def test_negative_reactivity_reduces_power():
    model = PointKinetics()
    model.set_reactivity(-0.001)

    initial = model.state().normalized_power
    final = model.advance(0.05).normalized_power

    assert final < initial


def test_time_accumulates():
    model = PointKinetics()
    model.advance(0.1)
    model.advance(0.2)

    assert model.state().time_s == pytest.approx(0.3)


def test_invalid_reactivity_is_rejected():
    model = PointKinetics()

    with pytest.raises(ValueError):
        model.set_reactivity(float("nan"))


def test_invalid_time_is_rejected():
    model = PointKinetics()

    with pytest.raises(ValueError):
        model.advance(-1.0)


def test_invalid_beta_is_rejected():
    with pytest.raises(ValueError):
        PointKinetics(beta=0.0)
