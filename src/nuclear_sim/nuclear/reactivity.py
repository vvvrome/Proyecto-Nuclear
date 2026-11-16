import math


def keff_to_reactivity(
    keff: float,
    reference_keff: float,
) -> float:
    """
    Calcula la reactividad diferencial respecto a un keff de referencia.

    La reactividad absoluta se define como:

        rho = (keff - 1) / keff

    Para evitar interpretar directamente los valores de keff del modelo
    simplificado de OpenMC como reactividad operativa absoluta, se calcula
    la diferencia respecto a un estado nominal:

        rho_diff = 1 / reference_keff - 1 / keff

    El estado de referencia produce rho_diff = 0.
    """
    if not math.isfinite(keff) or keff <= 0:
        raise ValueError("keff debe ser un valor finito mayor que cero.")

    if not math.isfinite(reference_keff) or reference_keff <= 0:
        raise ValueError(
            "reference_keff debe ser un valor finito mayor que cero."
        )

    return (1.0 / reference_keff) - (1.0 / keff)
