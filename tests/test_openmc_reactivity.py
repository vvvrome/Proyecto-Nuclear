import pytest

from nuclear_sim.nuclear.interpolation import (
    OpenMCInterpolator,
    OpenMCReferencePoint,
)

from nuclear_sim.nuclear.openmc_reactivity import (
    OpenMCReactivityModel,
    build_openmc_reactivity_model,
)

REFERENCE_KEFF = 1.3094440337578979


@pytest.fixture
def model():
    points = [
        OpenMCReferencePoint(
            u235_enrichment=3.5,
            keff=1.2964897814756546,
        ),
        OpenMCReferencePoint(
            u235_enrichment=4.0,
            keff=1.3094440337578979,
        ),
        OpenMCReferencePoint(
            u235_enrichment=4.5,
            keff=1.3412139507633685,
        ),
    ]

    interpolator = OpenMCInterpolator(points)

    return OpenMCReactivityModel(
        interpolator=interpolator,
        reference_keff=REFERENCE_KEFF,
    )


def test_reference_enrichment_has_zero_reactivity(model):
    rho = model.reactivity_for_enrichment(4.0)

    assert rho == pytest.approx(0.0)


def test_lower_enrichment_has_negative_reactivity(model):
    rho = model.reactivity_for_enrichment(3.5)

    assert rho < 0.0


def test_higher_enrichment_has_positive_reactivity(model):
    rho = model.reactivity_for_enrichment(4.5)

    assert rho > 0.0


def test_intermediate_enrichment_is_interpolated(model):
    rho = model.reactivity_for_enrichment(4.25)

    assert rho > 0.0


def test_enrichment_outside_reference_range_is_rejected(model):
    with pytest.raises(ValueError):
        model.reactivity_for_enrichment(3.0)

    with pytest.raises(ValueError):
        model.reactivity_for_enrichment(5.0)

class FakeOpenMCRepository:
    def get_openmc_reference_points(self):
        return [
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


def test_build_openmc_reactivity_model_from_repository():
    repository = FakeOpenMCRepository()

    model = build_openmc_reactivity_model(
        repository=repository,
        reference_keff=1.3094440337578979,
    )

    assert isinstance(model, OpenMCReactivityModel)
    assert model.reactivity_for_enrichment(4.0) == pytest.approx(0.0)


def test_build_openmc_reactivity_model_uses_repository_points():
    repository = FakeOpenMCRepository()

    model = build_openmc_reactivity_model(
        repository=repository,
        reference_keff=1.3094440337578979,
    )

    assert model.reactivity_for_enrichment(3.5) < 0.0
    assert model.reactivity_for_enrichment(4.5) > 0.0
