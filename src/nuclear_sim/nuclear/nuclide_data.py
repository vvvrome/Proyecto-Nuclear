
import json
import math
from pathlib import Path


# Cambios de Z y A exigidos por cada modo.
DECAY_RULES = {
    "beta_minus": (1, 0),
    "beta_plus": (-1, 0),
    "electron_capture": (-1, 0),
    "alpha": (-2, -4),
    "gamma": (0, 0),
    "isomeric_transition": (0, 0),
}



def validate_transition(parent: dict, daughter: dict, mode: str) -> None:
    """Comprueba la consistencia básica de una transición nuclear."""

    if mode not in DECAY_RULES:
        raise ValueError(f"Modo de desintegración desconocido: {mode}")

    delta_z, delta_a = DECAY_RULES[mode]

    expected_z = parent["atomic_number"] + delta_z
    expected_a = parent["mass_number"] + delta_a

    if daughter["atomic_number"] != expected_z:
        raise ValueError(
            f"Transición {parent['name']} -> {daughter['name']} "
            f"incompatible con {mode}: Z esperado {expected_z}, "
            f"obtenido {daughter['atomic_number']}."
        )

    if daughter["mass_number"] != expected_a:
        raise ValueError(
            f"Transición {parent['name']} -> {daughter['name']} "
            f"incompatible con {mode}: A esperado {expected_a}, "
            f"obtenido {daughter['mass_number']}."
        )



def load_nuclides(path: str | Path) -> dict[str, dict]:
    """Carga y valida un catálogo de núclidos desde JSON."""

    path = Path(path)

    with path.open("r", encoding="utf-8") as file:
        document = json.load(file)

    if document.get("schema_version") != 1:
        raise ValueError("Versión del esquema JSON no compatible.")



    source = document.get("source")
    records = document.get("nuclides")

    if not isinstance(source, dict) or not isinstance(records, list):
        raise ValueError("El catálogo debe incluir source y nuclides.")

    # Los metadatos básicos son obligatorios.
    for field in ("name",):
        value = source.get(field)

        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"El metadato source.{field} debe ser un texto no vacío."
            )

    # Los demás metadatos son opcionales para mantener compatibilidad
    # con los catálogos ficticios utilizados en las pruebas.
    for field in ("reference", "url", "data_status"):
        value = source.get(field)

        if value is not None and (
            not isinstance(value, str) or not value.strip()
        ):
            raise ValueError(
                f"El metadato source.{field} debe ser un texto no vacío."
            )

    url = source.get("url")

    if url is not None and not url.startswith(("https://", "http://")):
        raise ValueError(
            "La URL de la fuente debe utilizar HTTP o HTTPS."
        )


    catalog = {}

    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Cada núclido debe ser un objeto JSON.")

        name = record.get("name")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Nombre de núclido no válido.")

        if name in catalog:
            raise ValueError(f"Núclido duplicado: {name}")

        z = record.get("atomic_number")
        a = record.get("mass_number")
        half_life = record.get("half_life_s")
        energy = record.get("decay_energy_mev")
        branches = record.get("branches")
        
        energy_status = record.get("energy_status")

        allowed_energy_statuses = {
            "not_modelled",
            "partial_emission_model",
            "partial_emission_modelled",
            "stable",
        }

        if energy_status is not None:
            if (
                not isinstance(energy_status, str)
                or energy_status not in allowed_energy_statuses
            ):
                raise ValueError(
                    f"Estado energético no válido para {name}: "
                    f"{energy_status!r}."
                )

            if energy_status == "stable":
                if half_life is not None or branches:
                    raise ValueError(
                        f"El estado energético de {name} es 'stable', "
                        "pero el núclido no está definido como estable."
                    )

            elif half_life is None:
                raise ValueError(
                    f"El núclido estable {name} debe tener "
                    "energy_status='stable'."
                )

            
            if energy_status in {
                "partial_emission_model",
                "partial_emission_modelled",
            }:
                has_emission_energy = any(
                    "emitted_energy_mev" in branch
                    for branch in branches
                    if isinstance(branch, dict)
                )

                if not has_emission_energy:
                    raise ValueError(
                        f"{name} declara un modelo parcial de emisión, "
                        "pero ninguna rama contiene emitted_energy_mev."
                    )



        if (
            type(z) is not int
            or type(a) is not int
            or z < 0
            or a < 1
            or z > a
        ):
            raise ValueError(f"Números Z/A no válidos para {name}.")

        if half_life is not None and (
            isinstance(half_life, bool)
            or not isinstance(half_life, (int, float))
            or not math.isfinite(half_life)
            or half_life <= 0
        ):
            raise ValueError(f"Vida media no válida para {name}.")
        
        uncertainty_s = record.get("half_life_uncertainty_s")

        if uncertainty_s is not None:
            if (
                isinstance(uncertainty_s, bool)
                or not isinstance(uncertainty_s, (int, float))
                or not math.isfinite(uncertainty_s)
                or uncertainty_s < 0
            ):
                raise ValueError(
                    f"Incertidumbre de vida media no válida para {name}."
                )

            if half_life is None:
                raise ValueError(
                    f"El núclido estable {name} no debe tener "
                    "incertidumbre de vida media."
                )

            if uncertainty_s >= half_life:
                raise ValueError(
                    f"La incertidumbre de vida media de {name} "
                    "debe ser menor que su vida media."
                )

        if (
            isinstance(energy, bool)
            or not isinstance(energy, (int, float))
            or not math.isfinite(energy)
            or energy < 0
        ):
            raise ValueError(f"Energía no válida para {name}.")

        if not isinstance(branches, list):
            raise ValueError(f"Branches debe ser una lista en {name}.")

        if half_life is None and branches:
            raise ValueError(
                f"El núclido estable {name} no puede tener ramas."
            )

        total_fraction = 0.0

        for branch in branches:
            if not isinstance(branch, dict):
                raise ValueError(f"Rama no válida en {name}.")

            daughter = branch.get("daughter")
            fraction = branch.get("fraction")
            mode = branch.get("mode")

            if not isinstance(daughter, str) or not daughter:
                raise ValueError(f"Hijo no válido en {name}.")

            if (
                isinstance(fraction, bool)
                or not isinstance(fraction, (int, float))
                or not math.isfinite(fraction)
                or not 0 < fraction <= 1
            ):
                raise ValueError(f"Fracción no válida en {name}.")

            if not isinstance(mode, str) or not mode:
                raise ValueError(
                    f"Modo de desintegración no válido en {name}."
                )

            
            if mode not in DECAY_RULES:
                raise ValueError(
                    f"Modo de desintegración desconocido: {mode}"
                )

            emitted_energy = branch.get("emitted_energy_mev")
            deposition_fraction = branch.get("deposition_fraction")

            if emitted_energy is not None:
                if (
                    isinstance(emitted_energy, bool)
                    or not isinstance(emitted_energy, (int, float))
                    or not math.isfinite(emitted_energy)
                    or emitted_energy < 0
                ):
                    raise ValueError(
                        f"Energía emitida no válida en {name}."
                    )

            if deposition_fraction is not None:
                if (
                    isinstance(deposition_fraction, bool)
                    or not isinstance(deposition_fraction, (int, float))
                    or not math.isfinite(deposition_fraction)
                    or not 0 <= deposition_fraction <= 1
                ):
                    raise ValueError(
                        f"Fracción depositada no válida en {name}."
                    )

                if emitted_energy is None:
                    raise ValueError(
                        f"Hay fracción depositada sin energía en {name}."
                    )

            total_fraction += fraction


        if branches and not math.isclose(
            total_fraction, 1.0, rel_tol=0.0, abs_tol=1e-8
        ):
            raise ValueError(
                f"Las fracciones de las ramas de {name} deben sumar 1."
            )

        catalog[name] = record

    # Validar los enlaces una vez cargados todos los núclidos.
    for name, record in catalog.items():
        for branch in record["branches"]:
            daughter_name = branch["daughter"]

            if daughter_name not in catalog:
                raise ValueError(
                    f"El hijo {daughter_name} de {name} "
                    "no está en el catálogo."
                )

            if daughter_name == name:
                raise ValueError(
                    f"Ciclo directo de desintegración en {name}."
                )

            validate_transition(
                record,
                catalog[daughter_name],
                branch["mode"],
            )

    return catalog
