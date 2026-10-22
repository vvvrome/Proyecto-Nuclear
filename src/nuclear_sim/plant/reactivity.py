from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ReactivityState:
    """Estado de reactividad del reactor."""

    reactivity: float
    pcm: float
    dollars: float


class Reactivity:
    """Representación de la reactividad del reactor.

    La reactividad es:

        rho = (k_eff - 1) / k_eff

    La unidad pcm (per cent mille) se define como:

        1 pcm = 1e-5

    Los dólares utilizan la fracción retardada efectiva beta:

        rho_$ = rho / beta
    """

    def __init__(
        self,
        beta_effective: float = 0.0065,
    ) -> None:
        if (
            not math.isfinite(beta_effective)
            or not 0.0 < beta_effective < 1.0
        ):
            raise ValueError(
                "beta efectiva debe estar entre 0 y 1."
            )

        self.beta_effective = float(beta_effective)

    @staticmethod
    def from_keff(keff: float) -> float:
        """Calcula la reactividad a partir de k_eff."""

        if not math.isfinite(keff) or keff <= 0:
            raise ValueError(
                "k_eff debe ser positivo y finito."
            )

        return (keff - 1.0) / keff

    def state(self, reactivity: float) -> ReactivityState:
        """Convierte la reactividad a unidades útiles."""

        if not math.isfinite(reactivity):
            raise ValueError(
                "La reactividad debe ser finita."
            )

        pcm = reactivity * 100000.0
        dollars = reactivity / self.beta_effective

        return ReactivityState(
            reactivity=reactivity,
            pcm=pcm,
            dollars=dollars,
        )