import pytest

from nuclear_sim.plant.reactivity import Reactivity


def test_zero_reactivity():
    model = Reactivity()

    state = model.state(0.0)

    assert state.reactivity == pytest.approx(0.0)
    assert state.pcm == pytest.approx(0.0)
    assert state.dollars == pytest.approx(0.0)


def test_positive_reactivity_in_pcm():
    model = Reactivity()

    state = model.state(0.001)

    assert state.pcm == pytest.approx(100.0)


def test_negative_reactivity_in_pcm():
    model = Reactivity()

    state = model.state(-0.001)

    assert state.pcm == pytest.approx(-100.0)


def test_reactivity_in_dollars():
    model = Reactivity(beta_effective=0.0065)

    state = model.state(0.0065)

    assert state.dollars == pytest.approx(1.0)


def test_half_dollar_reactivity():
    model = Reactivity(beta_effective=0.0065)

    state = model.state(0.00325)

    assert state.dollars == pytest.approx(0.5)


def test_keff_one_is_critical():
    model = Reactivity()

    rho = model.from_keff(1.0)

    assert rho == pytest.approx(0.0)


def test_keff_above_one_is_positive():
    model = Reactivity()

    rho = model.from_keff(1.001)

    assert rho > 0.0


def test_keff_below_one_is_negative():
    model = Reactivity()

    rho = model.from_keff(0.999)

    assert rho < 0.0


def test_invalid_keff_is_rejected():
    model = Reactivity()

    with pytest.raises(ValueError):
        model.from_keff(0.0)


def test_invalid_beta_is_rejected():
    with pytest.raises(ValueError):
        Reactivity(beta_effective=0.0)


def test_nan_reactivity_is_rejected():
    model = Reactivity()

    with pytest.raises(ValueError):
        model.state(float("nan"))