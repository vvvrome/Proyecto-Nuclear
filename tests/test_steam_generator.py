import pytest

from nuclear_sim.thermal.steam_generator import SteamGenerator


def test_default_efficiency():
    generator = SteamGenerator()

    state = generator.generate(
        thermal_power_mw=1000.0,
        primary_temperature_k=573.15,
    )

    assert state.thermal_power_mw == pytest.approx(1000.0)
    assert state.steam_power_mw == pytest.approx(900.0)
    assert state.efficiency == pytest.approx(0.90)


def test_custom_efficiency():
    generator = SteamGenerator(efficiency=0.80)

    state = generator.generate(
        thermal_power_mw=1000.0,
        primary_temperature_k=573.15,
    )

    assert state.steam_power_mw == pytest.approx(800.0)


def test_higher_primary_temperature_increases_steam_temperature():
    generator = SteamGenerator()

    state = generator.generate(
        thermal_power_mw=1000.0,
        primary_temperature_k=673.15,
    )

    assert state.steam_temperature_k == pytest.approx(648.15)


def test_zero_power_produces_zero_steam_power():
    generator = SteamGenerator()

    state = generator.generate(
        thermal_power_mw=0.0,
        primary_temperature_k=573.15,
    )

    assert state.steam_power_mw == pytest.approx(0.0)


def test_negative_power_is_rejected():
    generator = SteamGenerator()

    with pytest.raises(ValueError):
        generator.generate(-1.0, 573.15)


def test_invalid_efficiency_is_rejected():
    with pytest.raises(ValueError):
        SteamGenerator(efficiency=0.0)


def test_invalid_temperature_is_rejected():
    generator = SteamGenerator()

    with pytest.raises(ValueError):
        generator.generate(1000.0, 0.0)