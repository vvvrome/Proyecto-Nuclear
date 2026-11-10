from __future__ import annotations

from pathlib import Path
import subprocess

from nuclear_sim.reactor.results import OpenMCResult, read_statepoint
from nuclear_sim.reactor.simulation import (
    ReactorSimulationConfig,
    create_pwr_model,
    export_model,
)


def run_openmc(
    output_directory: str | Path,
    config: ReactorSimulationConfig | None = None,
) -> OpenMCResult:
    """Ejecuta OpenMC y devuelve el resultado del statepoint generado."""

    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)

    model = create_pwr_model(config)
    export_model(model, output_path)

    subprocess.run(
        ["openmc"],
        cwd=output_path,
        check=True,
    )

    statepoints = sorted(output_path.glob("statepoint.*.h5"))

    if not statepoints:
        raise FileNotFoundError(
            f"OpenMC no generó ningún statepoint en {output_path}"
        )

    statepoint_path = statepoints[-1]

    return read_statepoint(statepoint_path)
