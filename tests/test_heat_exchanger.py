import pytest
import math
from nuclear_sim.thermal.heat_exchanger import HeatExchanger


def test_lmtd_for_equal_temperature_differences():
    exchanger = HeatExchanger(1000.0, 10.0)
    assert exchanger.lmtd(50.0, 50.0) == pytest.approx(50.0)


def test_lmtd_logarithmic_mean():
    exchanger = HeatExchanger(1000.0, 10.0)
    expected = (100.0 - 50.0) / __import__('math').log(100.0 / 50.0)
    assert exchanger.lmtd(100.0, 50.0) == pytest.approx(expected)


def test_heat_rate_is_u_a_lmtd():
    exchanger = HeatExchanger(1000.0, 10.0)
    state = exchanger.calculate(600.0, 550.0, 500.0, 510.0)
    assert state.heat_rate_w == pytest.approx(
        10000.0 * state.lmtd_k
    )


def test_invalid_temperature_difference_is_rejected():
    exchanger = HeatExchanger(1000.0, 10.0)
    with pytest.raises(ValueError):
        exchanger.lmtd(0.0, 50.0)


def test_invalid_u_is_rejected():
    with pytest.raises(ValueError):
        HeatExchanger(0.0, 10.0)

def test_log_mean_temperature_difference():
    exchanger = HeatExchanger(
        overall_heat_transfer_coefficient_w_m2_k=1000.0,
        heat_transfer_area_m2=100.0,
    )

    delta_t_lm = exchanger.log_mean_temperature_difference(
        hot_inlet_temperature_k=573.15,
        hot_outlet_temperature_k=513.15,
        cold_inlet_temperature_k=373.15,
        cold_outlet_temperature_k=423.15,
    )

    delta_t_1 = 573.15 - 423.15
    delta_t_2 = 513.15 - 373.15

    expected = (
        (delta_t_1 - delta_t_2)
        / math.log(delta_t_1 / delta_t_2)
    )

    assert delta_t_lm == pytest.approx(expected)


def test_equal_temperature_differences_return_that_difference():
    exchanger = HeatExchanger(
        overall_heat_transfer_coefficient_w_m2_k=1000.0,
        heat_transfer_area_m2=100.0,
    )

    delta_t_lm = exchanger.log_mean_temperature_difference(
        hot_inlet_temperature_k=500.0,
        hot_outlet_temperature_k=450.0,
        cold_inlet_temperature_k=350.0,
        cold_outlet_temperature_k=400.0,
    )

    assert delta_t_lm == pytest.approx(100.0)


def test_heat_transfer_is_calculated_from_ua_delta_tlm():
    exchanger = HeatExchanger(
        overall_heat_transfer_coefficient_w_m2_k=1000.0,
        heat_transfer_area_m2=100.0,
    )

    state = exchanger.transfer(
        hot_inlet_temperature_k=573.15,
        hot_outlet_temperature_k=523.15,
        cold_inlet_temperature_k=373.15,
        cold_outlet_temperature_k=423.15,
    )

    expected_delta_t_lm = (
        exchanger.log_mean_temperature_difference(
            hot_inlet_temperature_k=573.15,
            hot_outlet_temperature_k=523.15,
            cold_inlet_temperature_k=373.15,
            cold_outlet_temperature_k=423.15,
        )
    )

    expected_power_mw = (
        1000.0
        * 100.0
        * expected_delta_t_lm
        / 1.0e6
    )

    assert state.log_mean_temperature_difference_k == pytest.approx(
        expected_delta_t_lm
    )

    assert state.heat_transfer_mw == pytest.approx(
        expected_power_mw
    )


def test_heat_transfer_increases_with_area():
    small = HeatExchanger(
        overall_heat_transfer_coefficient_w_m2_k=1000.0,
        heat_transfer_area_m2=100.0,
    )

    large = HeatExchanger(
        overall_heat_transfer_coefficient_w_m2_k=1000.0,
        heat_transfer_area_m2=200.0,
    )

    small_state = small.transfer(
        hot_inlet_temperature_k=573.15,
        hot_outlet_temperature_k=523.15,
        cold_inlet_temperature_k=373.15,
        cold_outlet_temperature_k=423.15,
    )

    large_state = large.transfer(
        hot_inlet_temperature_k=573.15,
        hot_outlet_temperature_k=523.15,
        cold_inlet_temperature_k=373.15,
        cold_outlet_temperature_k=423.15,
    )

    assert large_state.heat_transfer_mw == pytest.approx(
        2.0 * small_state.heat_transfer_mw
    )


def test_heat_transfer_increases_with_overall_coefficient():
    low = HeatExchanger(
        overall_heat_transfer_coefficient_w_m2_k=500.0,
        heat_transfer_area_m2=100.0,
    )

    high = HeatExchanger(
        overall_heat_transfer_coefficient_w_m2_k=1000.0,
        heat_transfer_area_m2=100.0,
    )

    low_state = low.transfer(
        hot_inlet_temperature_k=573.15,
        hot_outlet_temperature_k=523.15,
        cold_inlet_temperature_k=373.15,
        cold_outlet_temperature_k=423.15,
    )

    high_state = high.transfer(
        hot_inlet_temperature_k=573.15,
        hot_outlet_temperature_k=523.15,
        cold_inlet_temperature_k=373.15,
        cold_outlet_temperature_k=423.15,
    )

    assert high_state.heat_transfer_mw == pytest.approx(
        2.0 * low_state.heat_transfer_mw
    )


def test_invalid_coefficient_is_rejected():
    with pytest.raises(ValueError):
        HeatExchanger(
            overall_heat_transfer_coefficient_w_m2_k=0.0,
            heat_transfer_area_m2=100.0,
        )


def test_invalid_area_is_rejected():
    with pytest.raises(ValueError):
        HeatExchanger(
            overall_heat_transfer_coefficient_w_m2_k=1000.0,
            heat_transfer_area_m2=0.0,
        )


def test_invalid_temperature_is_rejected():
    exchanger = HeatExchanger(
        overall_heat_transfer_coefficient_w_m2_k=1000.0,
        heat_transfer_area_m2=100.0,
    )

    with pytest.raises(ValueError):
        exchanger.transfer(
            hot_inlet_temperature_k=573.15,
            hot_outlet_temperature_k=523.15,
            cold_inlet_temperature_k=373.15,
            cold_outlet_temperature_k=-1.0,
        )


def test_invalid_temperature_difference_is_rejected():
    exchanger = HeatExchanger(
        overall_heat_transfer_coefficient_w_m2_k=1000.0,
        heat_transfer_area_m2=100.0,
    )

    with pytest.raises(ValueError):
        exchanger.transfer(
            hot_inlet_temperature_k=400.0,
            hot_outlet_temperature_k=350.0,
            cold_inlet_temperature_k=375.0,
            cold_outlet_temperature_k=425.0,
        )
