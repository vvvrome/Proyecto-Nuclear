from __future__ import annotations

import openmc

from nuclear_sim.reactor.materials import (
    ReactorMaterialConfig,
    create_pwr_materials,
)


FUEL_RADIUS_CM = 0.4096
GAP_OUTER_RADIUS_CM = 0.4180
CLADDING_OUTER_RADIUS_CM = 0.4750


def create_fuel_pin(
    materials: openmc.Materials,
) -> openmc.Universe:
    """
    Create a single PWR fuel pin.

    The pin consists of:
        - UO2 fuel
        - Helium gap
        - Zircaloy-4 cladding
        - Light-water moderator outside the cladding
    """
    fuel = materials[0]
    helium = materials[1]
    zircaloy = materials[2]
    water = materials[3]

    fuel_surface = openmc.ZCylinder(
        r=FUEL_RADIUS_CM,
        name="fuel_outer_surface",
    )

    gap_surface = openmc.ZCylinder(
        r=GAP_OUTER_RADIUS_CM,
        name="gap_outer_surface",
    )

    cladding_surface = openmc.ZCylinder(
        r=CLADDING_OUTER_RADIUS_CM,
        name="cladding_outer_surface",
    )

    fuel_cell = openmc.Cell(
        name="fuel",
        fill=fuel,
        region=-fuel_surface,
    )

    gap_cell = openmc.Cell(
        name="helium_gap",
        fill=helium,
        region=+fuel_surface & -gap_surface,
    )

    cladding_cell = openmc.Cell(
        name="cladding",
        fill=zircaloy,
        region=+gap_surface & -cladding_surface,
    )

    moderator_cell = openmc.Cell(
        name="moderator",
        fill=water,
        region=+cladding_surface,
    )

    universe = openmc.Universe(
        name="fuel_pin",
        cells=[
            fuel_cell,
            gap_cell,
            cladding_cell,
            moderator_cell,
        ],
    )

    return universe


def create_pwr_geometry(
    config: ReactorMaterialConfig | None = None,
) -> openmc.Geometry:
    """
    Create the OpenMC geometry for a single PWR fuel pin.
    """
    if config is None:
        config = ReactorMaterialConfig()

    materials = create_pwr_materials(config)
    fuel_pin = create_fuel_pin(materials)

    geometry = openmc.Geometry(fuel_pin)

    return geometry
