from dataclasses import dataclass


@dataclass(frozen=True)
class OpenMCReferencePoint:
    """Punto de referencia obtenido mediante OpenMC."""

    u235_enrichment: float
    keff: float


class OpenMCInterpolator:
    """Interpola linealmente keff a partir del enriquecimiento de U-235."""

    def __init__(self, points: list[OpenMCReferencePoint]):
        if len(points) < 2:
            raise ValueError(
                "Se necesitan al menos dos puntos de referencia OpenMC."
            )

        self._points = sorted(
            points,
            key=lambda point: point.u235_enrichment,
        )

    @property
    def minimum_enrichment(self) -> float:
        """Devuelve el enriquecimiento mínimo disponible."""
        return self._points[0].u235_enrichment

    @property
    def maximum_enrichment(self) -> float:
        """Devuelve el enriquecimiento máximo disponible."""
        return self._points[-1].u235_enrichment

    def interpolate_keff(self, enrichment: float) -> float:
        """Interpola keff para un enriquecimiento dentro del rango disponible."""

        if not (
            self.minimum_enrichment
            <= enrichment
            <= self.maximum_enrichment
        ):
            raise ValueError(
                "El enriquecimiento está fuera del rango de "
                f"referencia OpenMC: "
                f"{self.minimum_enrichment} - "
                f"{self.maximum_enrichment} %."
            )

        for left, right in zip(self._points, self._points[1:]):
            if left.u235_enrichment <= enrichment <= right.u235_enrichment:
                if left.u235_enrichment == right.u235_enrichment:
                    return left.keff

                fraction = (
                    enrichment - left.u235_enrichment
                ) / (
                    right.u235_enrichment - left.u235_enrichment
                )

                return left.keff + fraction * (
                    right.keff - left.keff
                )

        raise ValueError(
            f"No se pudo interpolar el enriquecimiento {enrichment} %."
        )


def build_openmc_interpolator(
    reference_points: list[dict],
) -> OpenMCInterpolator:
    """Construye un interpolador a partir de registros del repositorio."""

    points = [
        OpenMCReferencePoint(
            u235_enrichment=point["u235_enrichment"],
            keff=point["keff"],
        )
        for point in reference_points
    ]

    return OpenMCInterpolator(points)
