import pytest

from nuclear_sim.nuclear.interpolation import (
    OpenMCInterpolator,
    OpenMCReferencePoint,
)


def make_interpolator():
    return OpenMCInterpolator(
        [
            OpenMCReferencePoint(
                u235_enrichment=4.5,
                keff=1.3412139507633685,
            ),
            OpenMCReferencePoint(
                u235_enrichment=3.5,
                keff=1.2964897814756546,
            ),
            OpenMCReferencePoint(
                u235_enrichment=4.0,
                keff=1.3094440337578979,
            ),
        ]
    )


def test_interpolator_orders_reference_points():
    interpolator = make_interpolator()

    assert interpolator.minimum_enrichment == 3.5
    assert interpolator.maximum_enrichment == 4.5


def test_interpolator_returns_exact_reference_values():
    interpolator = make_interpolator()

    assert interpolator.interpolate_keff(3.5) == pytest.approx(
        1.2964897814756546
    )
    assert interpolator.interpolate_keff(4.0) == pytest.approx(
        1.3094440337578979
    )
    assert interpolator.interpolate_keff(4.5) == pytest.approx(
        1.3412139507633685
    )


def test_interpolator_calculates_intermediate_value():
    interpolator = make_interpolator()

    expected = (
        1.3094440337578979
        + 0.5 * (
            1.3412139507633685
            - 1.3094440337578979
        )
    )

    assert interpolator.interpolate_keff(4.25) == pytest.approx(
        expected
    )


def test_interpolator_rejects_enrichment_below_range():
    interpolator = make_interpolator()

    with pytest.raises(ValueError, match="fuera del rango"):
        interpolator.interpolate_keff(3.0)


def test_interpolator_rejects_enrichment_above_range():
    interpolator = make_interpolator()

    with pytest.raises(ValueError, match="fuera del rango"):
        interpolator.interpolate_keff(5.0)


def test_interpolator_requires_at_least_two_points():
    with pytest.raises(ValueError, match="al menos dos"):
        OpenMCInterpolator(
            [
                OpenMCReferencePoint(
                    u235_enrichment=4.0,
                    keff=1.3094440337578979,
                )
            ]
        )


def test_build_openmc_interpolator_from_repository_points():
    from nuclear_sim.nuclear.interpolation import build_openmc_interpolator

    reference_points = [
        {
            "u235_enrichment": 3.5,
            "keff": 1.2964897814756546,
        },
        {
            "u235_enrichment": 4.0,
            "keff": 1.3094440337578979,
        },
        {
            "u235_enrichment": 4.5,
            "keff": 1.3412139507633685,
        },
    ]

    interpolator = build_openmc_interpolator(reference_points)

    assert interpolator.minimum_enrichment == 3.5
    assert interpolator.maximum_enrichment == 4.5
    assert interpolator.interpolate_keff(4.0) == pytest.approx(
        1.3094440337578979
    )
