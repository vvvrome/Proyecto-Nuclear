from __future__ import annotations

from dataclasses import dataclass

import openmc


@dataclass(frozen=True)
class ReactorMaterialConfig:
    """Configuration parameters used to build PWR materials."""

    enrichment_u235: float = 4.0
    fuel_temperature: float = 900.0
    coolant_temperature: float = 573.0
    coolant_density: float = 0.743
    helium_density: float = 0.0016
    cladding_temperature: float = 573.0


def create_uo2(config: ReactorMaterialConfig) -> openmc.Material:
    """
    Create the UO2 fuel material.

    Parameters
    ----------
    config:
        Reactor material configuration.

    Returns
    -------
    openmc.Material
        UO2 fuel material.
    """
    if not 0.0 < config.enrichment_u235 < 100.0:
        raise ValueError("U-235 enrichment must be between 0 and 100 percent.")

    fuel = openmc.Material(name="UO2 fuel")
    fuel.set_density("g/cm3", 10.4)

    fuel.add_element(
        "U",
        1.0,
        enrichment=config.enrichment_u235,
    )
    fuel.add_element("O", 2.0)

    fuel.temperature = config.fuel_temperature

    return fuel


def create_helium(config: ReactorMaterialConfig) -> openmc.Material:
    """
    Create the helium gas used in the fuel-cladding gap.
    """
    helium = openmc.Material(name="Helium gap")
    helium.set_density("g/cm3", config.helium_density)
    helium.add_element("He", 1.0)
    helium.temperature = config.fuel_temperature

    return helium


def create_zircaloy4(config: ReactorMaterialConfig) -> openmc.Material:
    """
    Create the Zircaloy-4 cladding material.
    """
    zircaloy = openmc.Material(name="Zircaloy-4")
    zircaloy.set_density("g/cm3", 6.55)

    zircaloy.add_element("Zr", 1.0)

    zircaloy.temperature = config.cladding_temperature

    return zircaloy


def create_light_water(config: ReactorMaterialConfig) -> openmc.Material:
    """
    Create the light-water moderator/coolant.
    """
    water = openmc.Material(name="Light water")
    water.set_density("g/cm3", config.coolant_density)

    water.add_nuclide("H1", 2.0)
    water.add_nuclide("O16", 1.0)

    water.temperature = config.coolant_temperature

    return water


def create_pwr_materials(
    config: ReactorMaterialConfig | None = None,
) -> openmc.Materials:
    """
    Create the complete set of materials required by the simplified PWR.

    Parameters
    ----------
    config:
        Optional material configuration.

    Returns
    -------
    openmc.Materials
        OpenMC material collection.
    """
    if config is None:
        config = ReactorMaterialConfig()

    fuel = create_uo2(config)
    helium = create_helium(config)
    zircaloy = create_zircaloy4(config)
    water = create_light_water(config)

    materials = openmc.Materials(
        [
            fuel,
            helium,
            zircaloy,
            water,
        ]
    )

    return materials
