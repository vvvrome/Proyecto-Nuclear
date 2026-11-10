import openmc
import pytest

from nuclear_sim.reactor.settings import (
    SimulationConfig,
    create_initial_source,
    create_settings,
)


def test_default_configuration():
    config = SimulationConfig()

    assert config.batches == 50
    assert config.inactive == 10
    assert config.particles == 1000


def test_create_initial_source():
    source = create_initial_source()

    assert isinstance(source, openmc.IndependentSource)


def test_create_settings():
    settings = create_settings()

    assert isinstance(settings, openmc.Settings)
    assert settings.run_mode == "eigenvalue"
    assert settings.batches == 50
    assert settings.inactive == 10
    assert settings.particles == 1000


def test_custom_configuration():
    config = SimulationConfig(
        batches=100,
        inactive=20,
        particles=5000,
    )

    settings = create_settings(config)

    assert settings.batches == 100
    assert settings.inactive == 20
    assert settings.particles == 5000


@pytest.mark.parametrize(
    "config",
    [
        SimulationConfig(batches=0),
        SimulationConfig(batches=-1),
        SimulationConfig(batches=10, inactive=10),
        SimulationConfig(batches=10, inactive=11),
        SimulationConfig(particles=0),
        SimulationConfig(particles=-100),
    ],
)
def test_invalid_configuration(config):
    with pytest.raises(ValueError):
        create_settings(config)


def test_invalid_source_configuration():
    config = SimulationConfig(source_z_half_length_cm=0.0)

    with pytest.raises(ValueError):
        create_initial_source(config)


def test_settings_can_be_exported(tmp_path):
    settings = create_settings()

    settings_path = tmp_path / "settings.xml"

    settings.export_to_xml(path=str(settings_path))

    assert settings_path.exists()
