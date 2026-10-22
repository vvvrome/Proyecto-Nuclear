import pytest

from nuclear_sim.thermal.condenser import Condenser


def test_default_efficiency():
    condenser = Condenser()

    state = condenser.condense(
        steam_power_mw=100.0,
        mechanical_power_mw=80.0,
        inlet_temperature_k=473.15,
    )

    assert state.efficiency == pytest.approx(0.95)


def test_rejected_heat_is_steam_power_minus_mechanical_power():
    condenser = Condenser()

    state = condenser.condense(
        steam_power_mw=100.0,
        mechanical_power_mw=80.0,
        inlet_temperature_k=473.15,
    )

    assert state.rejected_heat_mw == pytest.approx(20.0)


def test_condensed_heat_respects_efficiency():
    condenser = Condenser(efficiency=0.90)

    state = condenser.condense(
        steam_power_mw=100.0,
        mechanical_power_mw=80.0,
        inlet_temperature_k=473.15,
    )

    assert state.condensed_heat_mw == pytest.approx(18.0)


def test_condensation_lowers_temperature():
    condenser = Condenser()

    state = condenser.condense(
        steam_power_mw=100.0,
        mechanical_power_mw=80.0,
        inlet_temperature_k=473.15,
    )

    assert state.outlet_temperature_k < state.inlet_temperature_k


def test_outlet_temperature_is_above_reference_for_hot_inlet():
    condenser = Condenser()

    state = condenser.condense(
        steam_power_mw=100.0,
        mechanical_power_mw=80.0,
        inlet_temperature_k=473.15,
    )

    assert (
        state.outlet_temperature_k
        > condenser.reference_temperature_k
    )


def test_zero_power_produces_zero_rejected_heat():
    condenser = Condenser()

    state = condenser.condense(
        steam_power_mw=0.0,
        mechanical_power_mw=0.0,
        inlet_temperature_k=473.15,
    )

    assert state.rejected_heat_mw == pytest.approx(0.0)
    assert state.condensed_heat_mw == pytest.approx(0.0)


def test_mechanical_power_cannot_exceed_steam_power():
    condenser = Condenser()

    with pytest.raises(ValueError):
        condenser.condense(
            steam_power_mw=50.0,
            mechanical_power_mw=60.0,
            inlet_temperature_k=473.15,
        )


def test_negative_steam_power_is_rejected():
    condenser = Condenser()

    with pytest.raises(ValueError):
        condenser.condense(
            steam_power_mw=-1.0,
            mechanical_power_mw=0.0,
            inlet_temperature_k=473.15,
        )


def test_negative_mechanical_power_is_rejected():
    condenser = Condenser()

    with pytest.raises(ValueError):
        condenser.condense(
            steam_power_mw=100.0,
            mechanical_power_mw=-1.0,
            inlet_temperature_k=473.15,
        )


def test_invalid_efficiency_is_rejected():
    with pytest.raises(ValueError):
        Condenser(efficiency=0.0)


def test_invalid_reference_temperature_is_rejected():
    with pytest.raises(ValueError):
        Condenser(reference_temperature_k=0.0)


def test_invalid_inlet_temperature_is_rejected():
    condenser = Condenser()

    with pytest.raises(ValueError):
        condenser.condense(
            steam_power_mw=100.0,
            mechanical_power_mw=80.0,
            inlet_temperature_k=0.0,
        )