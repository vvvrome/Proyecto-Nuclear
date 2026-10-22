import pytest

from nuclear_sim.nuclear.kinetics.temperature_feedback import (
    TemperatureFeedback,
)


def test_default_parameters():
    model = TemperatureFeedback()

    assert model.reference_temperature_k == pytest.approx(
        573.15
    )

    assert model.temperature_coefficient_per_k == pytest.approx(
        -1.0e-5
    )


def test_reference_temperature_has_zero_temperature_reactivity():
    model = TemperatureFeedback()

    reactivity = model.calculate_temperature_reactivity(
        573.15
    )

    assert reactivity == pytest.approx(0.0)


def test_higher_temperature_with_negative_coefficient_reduces_reactivity():
    model = TemperatureFeedback()

    reactivity = model.calculate_temperature_reactivity(
        673.15
    )

    assert reactivity < 0.0


def test_lower_temperature_with_negative_coefficient_increases_reactivity():
    model = TemperatureFeedback()

    reactivity = model.calculate_temperature_reactivity(
        473.15
    )

    assert reactivity > 0.0


def test_temperature_reactivity_is_linear():
    model = TemperatureFeedback(
        reference_temperature_k=500.0,
        temperature_coefficient_per_k=-2.0e-5,
    )

    reactivity = model.calculate_temperature_reactivity(
        550.0
    )

    assert reactivity == pytest.approx(-0.001)


def test_external_reactivity_is_added():
    model = TemperatureFeedback()

    total = model.calculate_total_reactivity(
        temperature_k=573.15,
        external_reactivity=0.002,
    )

    assert total == pytest.approx(0.002)


def test_total_reactivity_includes_temperature_effect():
    model = TemperatureFeedback(
        reference_temperature_k=573.15,
        temperature_coefficient_per_k=-1.0e-5,
    )

    total = model.calculate_total_reactivity(
        temperature_k=673.15,
        external_reactivity=0.002,
    )

    assert total == pytest.approx(0.001)


def test_state_contains_all_reactivity_components():
    model = TemperatureFeedback()

    state = model.state(
        temperature_k=673.15,
        external_reactivity=0.002,
    )

    assert state.temperature_k == pytest.approx(673.15)
    assert state.temperature_reactivity == pytest.approx(-0.001)
    assert state.external_reactivity == pytest.approx(0.002)
    assert state.total_reactivity == pytest.approx(0.001)


def test_non_finite_temperature_is_rejected():
    model = TemperatureFeedback()

    with pytest.raises(ValueError):
        model.calculate_temperature_reactivity(
            float("nan")
        )


def test_zero_temperature_is_rejected():
    model = TemperatureFeedback()

    with pytest.raises(ValueError):
        model.calculate_temperature_reactivity(0.0)


def test_invalid_reference_temperature_is_rejected():
    with pytest.raises(ValueError):
        TemperatureFeedback(
            reference_temperature_k=0.0
        )


def test_non_finite_coefficient_is_rejected():
    with pytest.raises(ValueError):
        TemperatureFeedback(
            temperature_coefficient_per_k=float("inf")
        )


def test_non_finite_external_reactivity_is_rejected():
    model = TemperatureFeedback()

    with pytest.raises(ValueError):
        model.calculate_total_reactivity(
            temperature_k=573.15,
            external_reactivity=float("nan"),
        )