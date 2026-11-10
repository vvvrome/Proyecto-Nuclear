from pathlib import Path

import pytest

from nuclear_sim.reactor.results import OpenMCResult, read_statepoint


STATEPOINT_PATH = Path("data/openmc/test_run/statepoint.50.h5")


def test_read_statepoint_returns_openmc_result():
    result = read_statepoint(STATEPOINT_PATH)

    assert isinstance(result, OpenMCResult)


def test_read_statepoint_reads_keff():
    result = read_statepoint(STATEPOINT_PATH)

    assert result.keff == pytest.approx(1.309444033757898)
    assert result.keff_std_dev == pytest.approx(0.004917954181157573)


def test_read_statepoint_reads_simulation_parameters():
    result = read_statepoint(STATEPOINT_PATH)

    assert result.batches == 50
    assert result.particles == 1000


def test_read_statepoint_path_is_preserved():
    result = read_statepoint(STATEPOINT_PATH)

    assert result.statepoint_path == STATEPOINT_PATH


def test_read_statepoint_missing_file():
    with pytest.raises(FileNotFoundError):
        read_statepoint("data/openmc/test_run/nonexistent.h5")
