import pytest

from nuclear_sim.plant.reactor import Reactor


def test_reactor_starts_shutdown():
    reactor = Reactor(rated_power_mw=3000)

    state = reactor.state()

    assert state.power_mw == 0.0
    assert state.status == "shutdown"


def test_reactor_can_set_power():
    reactor = Reactor(rated_power_mw=3000)

    reactor.set_power_fraction(0.5)

    state = reactor.state()

    assert state.power_mw == pytest.approx(1500.0)
    assert state.status == "operating"


def test_reactor_full_power():
    reactor = Reactor(rated_power_mw=3000)

    reactor.set_power_fraction(1.0)

    state = reactor.state()

    assert state.power_mw == pytest.approx(3000.0)
    assert state.status == "full_power"


def test_reactor_time_advances():
    reactor = Reactor(rated_power_mw=3000)

    reactor.advance(10.0)

    assert reactor.state().time_s == pytest.approx(10.0)


def test_negative_power_fraction_is_rejected():
    reactor = Reactor(rated_power_mw=3000)

    with pytest.raises(ValueError):
        reactor.set_power_fraction(-0.1)


def test_power_fraction_above_one_is_rejected():
    reactor = Reactor(rated_power_mw=3000)

    with pytest.raises(ValueError):
        reactor.set_power_fraction(1.1)


def test_invalid_rated_power_is_rejected():
    with pytest.raises(ValueError):
        Reactor(rated_power_mw=0)


def test_negative_time_is_rejected():
    reactor = Reactor(rated_power_mw=3000)

    with pytest.raises(ValueError):
        reactor.advance(-1.0)

def test_reactor_temperature_at_zero_power():
    reactor = Reactor(rated_power_mw=3000)

    state = reactor.state()

    assert state.temperature_k == pytest.approx(573.15)


def test_reactor_temperature_at_half_power():
    reactor = Reactor(rated_power_mw=3000)

    reactor.set_power_fraction(0.5)

    state = reactor.state()

    assert state.temperature_k == pytest.approx(673.15)


def test_reactor_temperature_at_full_power():
    reactor = Reactor(rated_power_mw=3000)

    reactor.set_power_fraction(1.0)

    state = reactor.state()

    assert state.temperature_k == pytest.approx(773.15)

def test_reactor_ramps_power_up():
    reactor = Reactor(rated_power_mw=3000)

    reactor.ramp_power(
        target_fraction=1.0,
        rate_per_s=0.1,
        dt_s=3.0,
    )

    assert reactor.state().power_mw == pytest.approx(900.0)


def test_reactor_ramps_power_down():
    reactor = Reactor(rated_power_mw=3000)

    reactor.set_power_fraction(1.0)

    reactor.ramp_power(
        target_fraction=0.0,
        rate_per_s=0.1,
        dt_s=4.0,
    )

    assert reactor.state().power_mw == pytest.approx(1800.0)


def test_reactor_reaches_target_power():
    reactor = Reactor(rated_power_mw=3000)

    reactor.ramp_power(
        target_fraction=0.5,
        rate_per_s=0.1,
        dt_s=10.0,
    )

    assert reactor.state().power_mw == pytest.approx(1500.0)


def test_ramp_power_does_not_overshoot_target():
    reactor = Reactor(rated_power_mw=3000)

    reactor.ramp_power(
        target_fraction=0.5,
        rate_per_s=0.5,
        dt_s=10.0,
    )

    assert reactor.state().power_mw == pytest.approx(1500.0)


def test_ramp_power_rejects_invalid_target():
    reactor = Reactor(rated_power_mw=3000)

    with pytest.raises(ValueError):
        reactor.ramp_power(
            target_fraction=1.5,
            rate_per_s=0.1,
            dt_s=1.0,
        )


def test_ramp_power_rejects_invalid_rate():
    reactor = Reactor(rated_power_mw=3000)

    with pytest.raises(ValueError):
        reactor.ramp_power(
            target_fraction=1.0,
            rate_per_s=0.0,
            dt_s=1.0,
        )


def test_ramp_power_rejects_negative_time():
    reactor = Reactor(rated_power_mw=3000)

    with pytest.raises(ValueError):
        reactor.ramp_power(
            target_fraction=1.0,
            rate_per_s=0.1,
            dt_s=-1.0,
        )

def test_scram_sets_power_to_zero():
    reactor = Reactor(rated_power_mw=3000)

    reactor.set_power_fraction(1.0)
    reactor.scram()

    assert reactor.state().power_mw == pytest.approx(0.0)


def test_scram_sets_shutdown_status():
    reactor = Reactor(rated_power_mw=3000)

    reactor.set_power_fraction(1.0)
    reactor.scram()

    assert reactor.state().status == "shutdown"


def test_scram_from_partial_power():
    reactor = Reactor(rated_power_mw=3000)

    reactor.set_power_fraction(0.65)
    reactor.scram()

    assert reactor.state().power_mw == pytest.approx(0.0)
    assert reactor.state().status == "shutdown"