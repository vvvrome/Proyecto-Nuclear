import pytest

from nuclear_sim.thermal.heat_exchanger import HeatExchanger


def create_exchanger() -> HeatExchanger:
    return HeatExchanger(
        overall_heat_transfer_coefficient_w_m2_k=1000.0,
        heat_transfer_area_m2=100.0,
    )


def test_solve_returns_positive_heat_transfer():
    exchanger = create_exchanger()

    state = exchanger.solve(
        hot_inlet_temperature_k=573.15,
        cold_inlet_temperature_k=373.15,
        hot_mass_flow_kg_s=1000.0,
        cold_mass_flow_kg_s=800.0,
        hot_specific_heat_kj_kg_k=4.18,
        cold_specific_heat_kj_kg_k=4.18,
    )

    assert state.heat_transfer_mw > 0.0


def test_hot_stream_cools():
    exchanger = create_exchanger()

    state = exchanger.solve(
        hot_inlet_temperature_k=573.15,
        cold_inlet_temperature_k=373.15,
        hot_mass_flow_kg_s=1000.0,
        cold_mass_flow_kg_s=800.0,
        hot_specific_heat_kj_kg_k=4.18,
        cold_specific_heat_kj_kg_k=4.18,
    )

    assert state.hot_outlet_temperature_k < (
        state.hot_inlet_temperature_k
    )


def test_cold_stream_heats():
    exchanger = create_exchanger()

    state = exchanger.solve(
        hot_inlet_temperature_k=573.15,
        cold_inlet_temperature_k=373.15,
        hot_mass_flow_kg_s=1000.0,
        cold_mass_flow_kg_s=800.0,
        hot_specific_heat_kj_kg_k=4.18,
        cold_specific_heat_kj_kg_k=4.18,
    )

    assert state.cold_outlet_temperature_k > (
        state.cold_inlet_temperature_k
    )


def test_energy_balance_hot_side():
    exchanger = create_exchanger()

    state = exchanger.solve(
        hot_inlet_temperature_k=573.15,
        cold_inlet_temperature_k=373.15,
        hot_mass_flow_kg_s=1000.0,
        cold_mass_flow_kg_s=800.0,
        hot_specific_heat_kj_kg_k=4.18,
        cold_specific_heat_kj_kg_k=4.18,
    )

    expected = (
        1000.0
        * 4.18
        / 1000.0
        * (
            state.hot_inlet_temperature_k
            - state.hot_outlet_temperature_k
        )
    )

    assert expected == pytest.approx(
        state.heat_transfer_mw,
        abs=1.0e-8,
    )


def test_energy_balance_cold_side():
    exchanger = create_exchanger()

    state = exchanger.solve(
        hot_inlet_temperature_k=573.15,
        cold_inlet_temperature_k=373.15,
        hot_mass_flow_kg_s=1000.0,
        cold_mass_flow_kg_s=800.0,
        hot_specific_heat_kj_kg_k=4.18,
        cold_specific_heat_kj_kg_k=4.18,
    )

    expected = (
        800.0
        * 4.18
        / 1000.0
        * (
            state.cold_outlet_temperature_k
            - state.cold_inlet_temperature_k
        )
    )

    assert expected == pytest.approx(
        state.heat_transfer_mw,
        abs=1.0e-8,
    )


def test_heat_transfer_is_limited_by_available_temperature_difference():
    exchanger = create_exchanger()

    state = exchanger.solve(
        hot_inlet_temperature_k=500.0,
        cold_inlet_temperature_k=490.0,
        hot_mass_flow_kg_s=1000.0,
        cold_mass_flow_kg_s=1000.0,
        hot_specific_heat_kj_kg_k=4.18,
        cold_specific_heat_kj_kg_k=4.18,
    )

    assert state.hot_outlet_temperature_k > (
        state.cold_inlet_temperature_k
    )

    assert state.cold_outlet_temperature_k < (
        state.hot_inlet_temperature_k
    )


def test_larger_heat_transfer_area_increases_heat_transfer():
    small = HeatExchanger(
        overall_heat_transfer_coefficient_w_m2_k=1000.0,
        heat_transfer_area_m2=50.0,
    )

    large = HeatExchanger(
        overall_heat_transfer_coefficient_w_m2_k=1000.0,
        heat_transfer_area_m2=100.0,
    )

    small_state = small.solve(
        hot_inlet_temperature_k=573.15,
        cold_inlet_temperature_k=373.15,
        hot_mass_flow_kg_s=1000.0,
        cold_mass_flow_kg_s=800.0,
        hot_specific_heat_kj_kg_k=4.18,
        cold_specific_heat_kj_kg_k=4.18,
    )

    large_state = large.solve(
        hot_inlet_temperature_k=573.15,
        cold_inlet_temperature_k=373.15,
        hot_mass_flow_kg_s=1000.0,
        cold_mass_flow_kg_s=800.0,
        hot_specific_heat_kj_kg_k=4.18,
        cold_specific_heat_kj_kg_k=4.18,
    )

    assert large_state.heat_transfer_mw > (
        small_state.heat_transfer_mw
    )


def test_invalid_hot_cold_temperature_order_is_rejected():
    exchanger = create_exchanger()

    with pytest.raises(ValueError):
        exchanger.solve(
            hot_inlet_temperature_k=373.15,
            cold_inlet_temperature_k=573.15,
            hot_mass_flow_kg_s=1000.0,
            cold_mass_flow_kg_s=800.0,
            hot_specific_heat_kj_kg_k=4.18,
            cold_specific_heat_kj_kg_k=4.18,
        )


def test_invalid_mass_flow_is_rejected():
    exchanger = create_exchanger()

    with pytest.raises(ValueError):
        exchanger.solve(
            hot_inlet_temperature_k=573.15,
            cold_inlet_temperature_k=373.15,
            hot_mass_flow_kg_s=0.0,
            cold_mass_flow_kg_s=800.0,
            hot_specific_heat_kj_kg_k=4.18,
            cold_specific_heat_kj_kg_k=4.18,
        )