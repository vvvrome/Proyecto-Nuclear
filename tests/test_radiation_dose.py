import pytest

from nuclear_sim.radiation.dose import DoseModel


def test_gray_is_joule_per_kg():
    state = DoseModel().calculate(10.0, 2.0)
    assert state.absorbed_dose_gy == pytest.approx(5.0)


def test_weighting_factor_gives_equivalent_dose():
    state = DoseModel(5.0).calculate(10.0, 2.0)
    assert state.equivalent_dose_sv == pytest.approx(25.0)


def test_zero_energy_gives_zero_dose():
    state = DoseModel().calculate(0.0, 2.0)
    assert state.absorbed_dose_gy == pytest.approx(0.0)


def test_invalid_mass_is_rejected():
    with pytest.raises(ValueError):
        DoseModel().calculate(10.0, 0.0)
