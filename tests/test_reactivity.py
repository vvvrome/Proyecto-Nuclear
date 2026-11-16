import math

import pytest

from nuclear_sim.nuclear.reactivity import keff_to_reactivity


REFERENCE_KEFF = 1.3094440337578979


def test_reference_keff_has_zero_differential_reactivity():
    rho = keff_to_reactivity(
        keff=REFERENCE_KEFF,
        reference_keff=REFERENCE_KEFF,
    )

    assert rho == pytest.approx(0.0)


def test_higher_keff_produces_positive_reactivity():
    rho = keff_to_reactivity(
        keff=1.34,
        reference_keff=REFERENCE_KEFF,
    )

    assert rho > 0.0


def test_lower_keff_produces_negative_reactivity():
    rho = keff_to_reactivity(
        keff=1.28,
        reference_keff=REFERENCE_KEFF,
    )

    assert rho < 0.0


@pytest.mark.parametrize("keff", [0.0, -1.0, math.inf, -math.inf, math.nan])
def test_invalid_keff_is_rejected(keff):
    with pytest.raises(ValueError):
        keff_to_reactivity(
            keff=keff,
            reference_keff=REFERENCE_KEFF,
        )


@pytest.mark.parametrize(
    "reference_keff",
    [0.0, -1.0, math.inf, -math.inf, math.nan],
)
def test_invalid_reference_keff_is_rejected(reference_keff):
    with pytest.raises(ValueError):
        keff_to_reactivity(
            keff=REFERENCE_KEFF,
            reference_keff=reference_keff,
        )
