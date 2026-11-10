from __future__ import annotations

from dataclasses import dataclass

import openmc


@dataclass(frozen=True)
class SimulationConfig:
    """Configuration parameters for an OpenMC eigenvalue simulation."""

    batches: int = 50
    inactive: int = 10
    particles: int = 1000
    source_z_half_length_cm: float = 1.0


def create_initial_source(
    config: SimulationConfig | None = None,
) -> openmc.IndependentSource:
    """
    Create the initial neutron source for the eigenvalue calculation.

    The initial source is placed at the center of the fuel pin.
    """
    if config is None:
        config = SimulationConfig()

    if config.source_z_half_length_cm <= 0.0:
        raise ValueError(
            "Source half-length must be greater than zero."
        )

    return openmc.IndependentSource(
        space=openmc.stats.Point((0.0, 0.0, 0.0)),
    )


def create_settings(
    config: SimulationConfig | None = None,
) -> openmc.Settings:
    """
    Create the OpenMC settings for the simplified PWR model.
    """
    if config is None:
        config = SimulationConfig()

    if config.batches <= 0:
        raise ValueError("Number of batches must be greater than zero.")

    if config.inactive < 0:
        raise ValueError("Number of inactive batches cannot be negative.")

    if config.inactive >= config.batches:
        raise ValueError(
            "Inactive batches must be lower than total batches."
        )

    if config.particles <= 0:
        raise ValueError("Number of particles must be greater than zero.")

    settings = openmc.Settings()

    settings.run_mode = "eigenvalue"
    settings.batches = config.batches
    settings.inactive = config.inactive
    settings.particles = config.particles
    settings.source = create_initial_source(config)
    settings.temperature = {
    	"method": "interpolation",
    	"tolerance": 1000.0,
    }
    return settings
