import pytest

from nuclear_sim.thermal.generator import Generator


def test_default_generator_efficiency():
    generator = Generator()

    state = generator.generate(1000.0)

    assert state.mechanical_power_mw == pytest.approx(1000.0)
    assert state.electrical_power_mw == pytest.approx(980.0)
    assert state.efficiency == pytest.approx(0.98)


def test_custom_efficiency():
    generator = Generator(efficiency=0.90)

    state = generator.generate(1000.0)

    assert state.electrical_power_mw == pytest.approx(900.0)


def test_zero_mechanical_power():
    generator = Generator()

    state = generator.generate(0.0)

    assert state.electrical_power_mw == pytest.approx(0.0)


def test_frequency_is_preserved():
    generator = Generator(frequency_hz=60.0)

    state = generator.generate(100.0)

    assert state.frequency_hz == pytest.approx(60.0)


def test_negative_mechanical_power_is_rejected():
    generator = Generator()

    with pytest.raises(ValueError):
        generator.generate(-1.0)


def test_invalid_efficiency_is_rejected():
    with pytest.raises(ValueError):
        Generator(efficiency=0.0)


def test_invalid_frequency_is_rejected():
    with pytest.raises(ValueError):
        Generator(frequency_hz=0.0)