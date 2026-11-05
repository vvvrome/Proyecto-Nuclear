import openmc
import pytest

from nuclear_sim.reactor.materials import (
    ReactorMaterialConfig,
    create_pwr_materials,
    create_uo2,
)


def test_create_pwr_materials():
    materials = create_pwr_materials()

    assert isinstance(materials, openmc.Materials)
    assert len(materials) == 4


def test_material_names():
    materials = create_pwr_materials()

    names = {material.name for material in materials}

    assert names == {
        "UO2 fuel",
        "Helium gap",
        "Zircaloy-4",
        "Light water",
    }


def test_default_enrichment():
    config = ReactorMaterialConfig(enrichment_u235=4.0)

    fuel = create_uo2(config)

    assert fuel.name == "UO2 fuel"


@pytest.mark.parametrize("enrichment", [-1.0, 0.0, 100.0, 101.0])
def test_invalid_enrichment(enrichment):
    config = ReactorMaterialConfig(enrichment_u235=enrichment)

    with pytest.raises(ValueError):
        create_uo2(config)
