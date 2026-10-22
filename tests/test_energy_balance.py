import pytest

from nuclear_sim.thermal.energy_balance import EnergyBalance


def test_energy_balance_closes():
    balance = EnergyBalance()

    state = balance.calculate(
        input_power_mw=1000.0,
        thermal_losses_mw=20.0,
        useful_thermal_power_mw=980.0,
        steam_power_mw=882.0,
        mechanical_power_mw=749.7,
        electrical_power_mw=734.706,
        rejected_heat_mw=132.3,
        auxiliary_power_mw=10.0,
    )

    assert state.balance_error_mw == pytest.approx(0.0)


def test_net_electrical_power_is_gross_minus_auxiliary():
    balance = EnergyBalance()

    state = balance.calculate(
        input_power_mw=1000.0,
        thermal_losses_mw=20.0,
        useful_thermal_power_mw=980.0,
        steam_power_mw=882.0,
        mechanical_power_mw=749.7,
        electrical_power_mw=734.706,
        rejected_heat_mw=132.3,
        auxiliary_power_mw=10.0,
    )

    assert state.net_electrical_power_mw == pytest.approx(
        724.706
    )


def test_losses_are_calculated():
    balance = EnergyBalance()

    state = balance.calculate(
        input_power_mw=1000.0,
        thermal_losses_mw=20.0,
        useful_thermal_power_mw=980.0,
        steam_power_mw=882.0,
        mechanical_power_mw=749.7,
        electrical_power_mw=734.706,
        rejected_heat_mw=132.3,
        auxiliary_power_mw=10.0,
    )

    assert state.steam_generation_losses_mw == pytest.approx(
        98.0
    )

    assert state.turbine_losses_mw == pytest.approx(
        132.3
    )

    assert state.generator_losses_mw == pytest.approx(
        14.994
    )


def test_efficiencies_are_calculated():
    balance = EnergyBalance()

    state = balance.calculate(
        input_power_mw=1000.0,
        thermal_losses_mw=20.0,
        useful_thermal_power_mw=980.0,
        steam_power_mw=882.0,
        mechanical_power_mw=749.7,
        electrical_power_mw=734.706,
        rejected_heat_mw=132.3,
        auxiliary_power_mw=10.0,
    )

    assert state.thermal_efficiency == pytest.approx(
        0.734706
    )

    assert state.net_efficiency == pytest.approx(
        0.724706
    )


def test_zero_input_power():
    balance = EnergyBalance()

    state = balance.calculate(
        input_power_mw=0.0,
        thermal_losses_mw=0.0,
        useful_thermal_power_mw=0.0,
        steam_power_mw=0.0,
        mechanical_power_mw=0.0,
        electrical_power_mw=0.0,
        rejected_heat_mw=0.0,
        auxiliary_power_mw=0.0,
    )

    assert state.balance_error_mw == pytest.approx(0.0)
    assert state.thermal_efficiency == pytest.approx(0.0)
    assert state.net_efficiency == pytest.approx(0.0)


def test_negative_values_are_rejected():
    balance = EnergyBalance()

    with pytest.raises(ValueError):
        balance.calculate(
            input_power_mw=-1.0,
            thermal_losses_mw=0.0,
            useful_thermal_power_mw=0.0,
            steam_power_mw=0.0,
            mechanical_power_mw=0.0,
            electrical_power_mw=0.0,
            rejected_heat_mw=0.0,
            auxiliary_power_mw=0.0,
        )


def test_impossible_power_hierarchy_is_rejected():
    balance = EnergyBalance()

    with pytest.raises(ValueError):
        balance.calculate(
            input_power_mw=1000.0,
            thermal_losses_mw=20.0,
            useful_thermal_power_mw=980.0,
            steam_power_mw=1000.0,
            mechanical_power_mw=800.0,
            electrical_power_mw=700.0,
            rejected_heat_mw=200.0,
            auxiliary_power_mw=10.0,
        )