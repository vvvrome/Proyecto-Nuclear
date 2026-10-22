import pytest

from nuclear_sim.nuclear.kinetics.point_kinetics import PointKinetics


def test_initial_parameters():
    model = PointKinetics()

    assert model.beta == pytest.approx(0.0065)
    assert model.generation_time_s == pytest.approx(1.0e-4)
    assert model.precursor_decay_constant_per_s == pytest.approx(0.08)


def test_critical_reactor_has_zero_prompt_derivative():
    model = PointKinetics()

    dn_dt, dC_dt = model.derivatives(
        neutron_population=1.0,
        precursor_population=0.0,
        reactivity=0.0,
    )

    assert dn_dt < 0.0
    assert dC_dt > 0.0


def test_positive_reactivity_increases_neutron_population():
    model = PointKinetics()

    dn_dt, _ = model.derivatives(
        neutron_population=1.0,
        precursor_population=1.0,
        reactivity=0.01,
    )

    assert dn_dt > 0.0


def test_negative_reactivity_decreases_neutron_population():
    model = PointKinetics()

    dn_dt, _ = model.derivatives(
        neutron_population=1.0,
        precursor_population=0.0,
        reactivity=-0.01,
    )

    assert dn_dt < 0.0


def test_precursor_population_is_produced_by_neutrons():
    model = PointKinetics()

    _, dC_dt = model.derivatives(
        neutron_population=1.0,
        precursor_population=0.0,
        reactivity=0.0,
    )

    assert dC_dt > 0.0


def test_precursor_decay_reduces_precursors():
    model = PointKinetics()

    _, dC_dt = model.derivatives(
        neutron_population=0.0,
        precursor_population=10.0,
        reactivity=0.0,
    )

    assert dC_dt < 0.0


def test_zero_time_preserves_state():
    model = PointKinetics()

    state = model.step(
        neutron_population=1.0,
        precursor_population=2.0,
        reactivity=0.0,
        dt_s=0.0,
    )

    assert state.neutron_population == pytest.approx(1.0)
    assert state.precursor_population == pytest.approx(2.0)


def test_positive_reactivity_increases_population():
    model = PointKinetics(
        generation_time_s=0.01,
    )

    state = model.step(
        neutron_population=1.0,
        precursor_population=0.0,
        reactivity=0.01,
        dt_s=0.001,
    )

    assert state.neutron_population > 1.0


def test_negative_reactivity_reduces_population():
    model = PointKinetics(
        generation_time_s=0.01,
    )

    state = model.step(
        neutron_population=1.0,
        precursor_population=0.0,
        reactivity=-0.01,
        dt_s=0.001,
    )

    assert state.neutron_population < 1.0


def test_negative_time_is_rejected():
    model = PointKinetics()

    with pytest.raises(ValueError):
        model.step(
            neutron_population=1.0,
            precursor_population=1.0,
            reactivity=0.0,
            dt_s=-1.0,
        )


def test_negative_neutron_population_is_rejected():
    model = PointKinetics()

    with pytest.raises(ValueError):
        model.derivatives(
            neutron_population=-1.0,
            precursor_population=1.0,
            reactivity=0.0,
        )


def test_negative_precursor_population_is_rejected():
    model = PointKinetics()

    with pytest.raises(ValueError):
        model.derivatives(
            neutron_population=1.0,
            precursor_population=-1.0,
            reactivity=0.0,
        )


def test_invalid_beta_is_rejected():
    with pytest.raises(ValueError):
        PointKinetics(beta=0.0)


def test_invalid_generation_time_is_rejected():
    with pytest.raises(ValueError):
        PointKinetics(generation_time_s=0.0)


def test_invalid_decay_constant_is_rejected():
    with pytest.raises(ValueError):
        PointKinetics(
            precursor_decay_constant_per_s=0.0
        )

def test_equilibrium_precursor_population():
    model = PointKinetics()

    neutron_population = 1.0

    expected = (
        model.beta
        / (
            model.generation_time_s
            * model.precursor_decay_constant_per_s
        )
        * neutron_population
    )

    result = model.equilibrium_precursor_population(
        neutron_population
    )

    assert result == pytest.approx(expected)


def test_equilibrium_state_has_zero_derivatives():
    model = PointKinetics()

    state = model.equilibrium_state(
        neutron_population=1.0
    )

    dn_dt, dC_dt = model.derivatives(
        neutron_population=state.neutron_population,
        precursor_population=state.precursor_population,
        reactivity=0.0,
    )

    assert dn_dt == pytest.approx(0.0, abs=1e-12)
    assert dC_dt == pytest.approx(0.0, abs=1e-12)


def test_equilibrium_state_preserves_neutron_population():
    model = PointKinetics()

    initial = model.equilibrium_state(
        neutron_population=1.0
    )

    final = model.step(
        neutron_population=initial.neutron_population,
        precursor_population=initial.precursor_population,
        reactivity=0.0,
        dt_s=1e-5,
    )

    assert final.neutron_population == pytest.approx(
        initial.neutron_population,
        rel=1e-6,
    )

    assert final.precursor_population == pytest.approx(
        initial.precursor_population,
        rel=1e-6,
    )


def test_equilibrium_precursor_population_scales_with_neutrons():
    model = PointKinetics()

    state_1 = model.equilibrium_precursor_population(1.0)
    state_2 = model.equilibrium_precursor_population(2.0)

    assert state_2 == pytest.approx(2.0 * state_1)


def test_equilibrium_rejects_negative_neutron_population():
    model = PointKinetics()

    with pytest.raises(ValueError):
        model.equilibrium_precursor_population(-1.0)


def test_rk4_produces_positive_population_for_positive_reactivity():
    model = PointKinetics(
        generation_time_s=0.01,
    )

    state = model.equilibrium_state(
        neutron_population=1.0
    )

    final = model.step(
        neutron_population=state.neutron_population,
        precursor_population=state.precursor_population,
        reactivity=0.001,
        dt_s=0.001,
    )

    assert final.neutron_population > 1.0


def test_rk4_reduces_population_for_negative_reactivity():
    model = PointKinetics(
        generation_time_s=0.01,
    )

    state = model.equilibrium_state(
        neutron_population=1.0
    )

    final = model.step(
        neutron_population=state.neutron_population,
        precursor_population=state.precursor_population,
        reactivity=-0.001,
        dt_s=0.001,
    )

    assert final.neutron_population < 1.0