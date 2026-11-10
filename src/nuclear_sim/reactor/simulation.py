from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import openmc

from nuclear_sim.reactor.geometry import create_pwr_geometry
from nuclear_sim.reactor.materials import (
    ReactorMaterialConfig,
    create_pwr_materials,
)
from nuclear_sim.reactor.settings import (
    SimulationConfig,
    create_settings,
)


@dataclass(frozen=True)
class ReactorSimulationConfig:
    """Configuration for a complete PWR OpenMC simulation."""

    materials: ReactorMaterialConfig = ReactorMaterialConfig()
    simulation: SimulationConfig = SimulationConfig()


def create_pwr_model(
    config: ReactorSimulationConfig | None = None,
) -> openmc.Model:
    """
    Build the complete OpenMC model for the simplified PWR.
    """
    if config is None:
        config = ReactorSimulationConfig()

    materials = create_pwr_materials(config.materials)
    geometry = create_pwr_geometry(materials)
    settings = create_settings(config.simulation)

    return openmc.Model(
        geometry=geometry,
        materials=materials,
        settings=settings,
    )


def export_model(
    model: openmc.Model,
    output_directory: str | Path,
) -> Path:
    """
    Export the OpenMC model XML files to a directory.
    """
    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)

    model.export_to_xml(
        directory=str(output_path),
    )

    return output_path
