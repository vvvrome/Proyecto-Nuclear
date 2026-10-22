import pytest

from nuclear_sim.thermal.thermal_losses import (
    ThermalLossModel,
)


def test_no_losses():
    losses = ThermalLossModel(
        loss_fraction=0.0,
    )

    state = losses.calculate(
        input_power_mw=1000.0,
    )

    assert state.lost_power_mw == pytest.approx(0.0)
    assert state.useful_power_mw == pytest.approx(1000.0)


def test_losses_are_calculated():
    losses = ThermalLossModel(
        loss_fraction=0.02,
    )

    state = losses.calculate(
        input_power_mw=1000.0,
    )

    assert state.lost_power_mw == pytest.approx(20.0)
    assert state.useful_power_mw == pytest.approx(980.0)


def test_energy_balance_is_preserved():
    losses = ThermalLossModel(
        loss_fraction=0.05,
    )

    state = losses.calculate(
        input_power_mw=1000.0,
    )

    assert (
        state.useful_power_mw
        + state.lost_power_mw
    ) == pytest.approx(
        state.input_power_mw
    )


def test_higher_losses_reduce_useful_power():
    low = ThermalLossModel(
        loss_fraction=0.01,
    )

    high = ThermalLossModel(
        loss_fraction=0.10,
    )

    low_state = low.calculate(
        input_power_mw=1000.0,
    )

    high_state = high.calculate(
        input_power_mw=1000.0,
    )

    assert high_state.useful_power_mw < (
        low_state.useful_power_mw
    )


def test_zero_power_produces_zero_losses():
    losses = ThermalLossModel(
        loss_fraction=0.05,
    )

    state = losses.calculate(
        input_power_mw=0.0,
    )

    assert state.lost_power_mw == pytest.approx(0.0)
    assert state.useful_power_mw == pytest.approx(0.0)


def test_invalid_loss_fraction_is_rejected():
    with pytest.raises(ValueError):
        ThermalLossModel(
            loss_fraction=-0.01,
        )

    with pytest.raises(ValueError):
        ThermalLossModel(
            loss_fraction=1.0,
        )


def test_invalid_power_is_rejected():
    losses = ThermalLossModel()

    with pytest.raises(ValueError):
        losses.calculate(
            input_power_mw=-1.0,
        )