from __future__ import annotations

import openmc


FUEL_RADIUS_CM = 0.4096
GAP_OUTER_RADIUS_CM = 0.4180
CLADDING_OUTER_RADIUS_CM = 0.4750
MODERATOR_OUTER_RADIUS_CM = 0.63

AXIAL_HALF_LENGTH_CM = 0.5


def create_fuel_pin(
    materials: openmc.Materials,
) -> openmc.Universe:
    """
    Create a single PWR fuel pin inside a finite reflective cell.

    The pin consists of:
        - UO2 fuel
        - Helium gap
        - Zircaloy-4 cladding
        - Light-water moderator

    The outer radial and axial boundaries are reflective, representing
    a simplified repeating fuel cell.
    """

    fuel = materials[0]
    helium = materials[1]
    zircaloy = materials[2]
    water = materials[3]

    # Radial surfaces
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

    outer_surface = openmc.ZCylinder(
        r=MODERATOR_OUTER_RADIUS_CM,
        name="cell_outer_surface",
        boundary_type="reflective",
    )

    # Axial surfaces
    bottom_surface = openmc.ZPlane(
        z0=-AXIAL_HALF_LENGTH_CM,
        name="cell_bottom_surface",
        boundary_type="reflective",
    )

    top_surface = openmc.ZPlane(
        z0=AXIAL_HALF_LENGTH_CM,
        name="cell_top_surface",
        boundary_type="reflective",
    )

    axial_region = +bottom_surface & -top_surface

    # Fuel
    fuel_cell = openmc.Cell(
        name="fuel",
        fill=fuel,
        region=-fuel_surface & axial_region,
    )

    # Helium gap
    gap_cell = openmc.Cell(
        name="helium_gap",
        fill=helium,
        region=(
            +fuel_surface
            & -gap_surface
            & axial_region
        ),
    )

    # Zircaloy cladding
    cladding_cell = openmc.Cell(
        name="cladding",
        fill=zircaloy,
        region=(
            +gap_surface
            & -cladding_surface
            & axial_region
        ),
    )

    # Moderator
    moderator_cell = openmc.Cell(
        name="moderator",
        fill=water,
        region=(
            +cladding_surface
            & -outer_surface
            & axial_region
        ),
    )

    return openmc.Universe(
        name="fuel_pin",
        cells=[
            fuel_cell,
            gap_cell,
            cladding_cell,
            moderator_cell,
        ],
    )


def create_pwr_geometry(
    materials: openmc.Materials,
) -> openmc.Geometry:
    """
    Create the OpenMC geometry for a single simplified PWR fuel cell.
    """
    fuel_pin = create_fuel_pin(materials)

    return openmc.Geometry(fuel_pin)
