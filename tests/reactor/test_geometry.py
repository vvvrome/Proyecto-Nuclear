import openmc
import pytest

from nuclear_sim.reactor.geometry import (
    CLADDING_OUTER_RADIUS_CM,
    FUEL_RADIUS_CM,
    GAP_OUTER_RADIUS_CM,
    create_fuel_pin,
    create_pwr_geometry,
)
from nuclear_sim.reactor.materials import create_pwr_materials


def test_fuel_pin_is_universe():
    materials = create_pwr_materials()

    universe = create_fuel_pin(materials)

    assert isinstance(universe, openmc.Universe)


def test_fuel_pin_has_four_cells():
    materials = create_pwr_materials()

    universe = create_fuel_pin(materials)

    assert len(universe.cells) == 4


def test_fuel_pin_cell_names():
    materials = create_pwr_materials()

    universe = create_fuel_pin(materials)

    names = {cell.name for cell in universe.cells.values()}

    assert names == {
        "fuel",
        "helium_gap",
        "cladding",
        "moderator",
    }


def test_radii_are_ordered():
    assert 0 < FUEL_RADIUS_CM
    assert FUEL_RADIUS_CM < GAP_OUTER_RADIUS_CM
    assert GAP_OUTER_RADIUS_CM < CLADDING_OUTER_RADIUS_CM


def test_create_pwr_geometry():
    geometry = create_pwr_geometry()

    assert isinstance(geometry, openmc.Geometry)
    assert geometry.root_universe is not None


def test_geometry_contains_fuel_pin():
    geometry = create_pwr_geometry()

    root_universe = geometry.root_universe

    assert len(root_universe.cells) == 4


def test_geometry_can_be_exported(tmp_path):
    geometry = create_pwr_geometry()

    geometry.export_to_xml(
        path=str(tmp_path / "geometry.xml"),
    )

    assert (tmp_path / "geometry.xml").exists()
