from pathlib import Path

import openmc

from nuclear_sim.reactor.simulation import (
    ReactorSimulationConfig,
    create_pwr_model,
    export_model,
)


def test_create_pwr_model():
    model = create_pwr_model()

    assert isinstance(model, openmc.Model)
    assert model.geometry is not None
    assert model.materials is not None
    assert model.settings is not None


def test_model_has_expected_materials():
    model = create_pwr_model()

    assert len(model.materials) == 4


def test_model_has_expected_geometry():
    model = create_pwr_model()

    assert model.geometry.root_universe is not None
    assert len(model.geometry.root_universe.cells) == 4


def test_model_has_eigenvalue_settings():
    model = create_pwr_model()

    assert model.settings.run_mode == "eigenvalue"
    assert model.settings.batches == 50
    assert model.settings.inactive == 10
    assert model.settings.particles == 1000


def test_export_model(tmp_path):
    model = create_pwr_model()

    output_directory = export_model(
        model,
        tmp_path / "openmc",
    )

    assert isinstance(output_directory, Path)

    assert (output_directory / "materials.xml").exists()
    assert (output_directory / "geometry.xml").exists()
    assert (output_directory / "settings.xml").exists()
