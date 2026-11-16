from nuclear_sim.nuclear.interpolation import (
    OpenMCInterpolator,
    build_openmc_interpolator,
)
from nuclear_sim.nuclear.reactivity import (
    keff_to_reactivity,
)


class OpenMCReactivityModel:
    """Modelo de reactividad basado en referencias interpoladas de OpenMC."""

    def __init__(
        self,
        interpolator: OpenMCInterpolator,
        reference_keff: float,
    ) -> None:
        self.interpolator = interpolator
        self.reference_keff = reference_keff

    def reactivity_for_enrichment(
        self,
        enrichment: float,
    ) -> float:
        """Devuelve la reactividad diferencial para un enriquecimiento dado."""

        keff = self.interpolator.interpolate_keff(enrichment)

        return keff_to_reactivity(
            keff=keff,
            reference_keff=self.reference_keff,
        )


def build_openmc_reactivity_model(
    repository,
    reference_keff: float,
) -> OpenMCReactivityModel:
    """Construye el modelo de reactividad a partir de referencias del repositorio."""

    reference_points = repository.get_openmc_reference_points()

    interpolator = build_openmc_interpolator(
        reference_points
    )

    return OpenMCReactivityModel(
        interpolator=interpolator,
        reference_keff=reference_keff,
    )
