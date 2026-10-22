import math
from pathlib import Path
import json
import pytest

from nuclear_sim.nuclear.nuclide_data import load_nuclides


CATALOG_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "nuclear"
    / "nuclides.json"
)

@pytest.fixture
def catalog_file(tmp_path):
    document = json.loads(
        CATALOG_PATH.read_text(encoding="utf-8")
    )
    path = tmp_path / "nuclides.json"
    path.write_text(
        json.dumps(document),
        encoding="utf-8",
    )
    return path


@pytest.fixture
def catalog():
    return load_nuclides(CATALOG_PATH)


def test_real_catalog_contains_expected_nuclides(catalog):
    assert {"Cs-137", "Ba-137m", "Ba-137"} <= set(catalog)


def test_half_life_uncertainties_are_consistent(catalog):
    assert catalog["Cs-137"]["half_life_uncertainty_s"] == pytest.approx(
        2_840_184.0
    )
    assert catalog["Ba-137m"]["half_life_uncertainty_s"] == pytest.approx(
        0.6
    )


def test_branch_fractions_sum_to_one(catalog):
    for name, record in catalog.items():
        if record["branches"]:
            assert sum(
                branch["fraction"] for branch in record["branches"]
            ) == pytest.approx(1.0)


def test_all_real_catalog_transitions_are_valid(catalog):
    from nuclear_sim.nuclear.nuclide_data import validate_transition

    for name, record in catalog.items():
        for branch in record["branches"]:
            daughter = catalog[branch["daughter"]]
            validate_transition(record, daughter, branch["mode"])


def test_stable_barium_has_no_decay_branches(catalog):
    barium = catalog["Ba-137"]

    assert barium["half_life_s"] is None
    assert barium["branches"] == []


import copy
import json

import pytest


def test_rejects_unknown_energy_status(catalog_file):
    document = json.loads(catalog_file.read_text(encoding="utf-8"))
    document["nuclides"][0]["energy_status"] = "fully_magic"

    catalog_file.write_text(
        json.dumps(document),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Estado energético no válido"):
        load_nuclides(catalog_file)


def test_rejects_partial_model_without_emission_energy(catalog_file):
    document = json.loads(catalog_file.read_text(encoding="utf-8"))
    record = document["nuclides"][0]
    record["energy_status"] = "partial_emission_modelled"

    for branch in record["branches"]:
        branch.pop("emitted_energy_mev", None)

    catalog_file.write_text(
        json.dumps(document),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="ninguna rama contiene emitted_energy_mev",
    ):
        load_nuclides(catalog_file)


def test_rejects_stable_status_for_radioactive_nuclide(catalog_file):
    document = json.loads(catalog_file.read_text(encoding="utf-8"))
    record = document["nuclides"][0]
    record["energy_status"] = "stable"

    catalog_file.write_text(
        json.dumps(document),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="no está definido como estable"):
        load_nuclides(catalog_file)
