
import json

import pytest

from nuclear_sim.nuclear.nuclide_data import load_nuclides


def make_document(uncertainty):
    return {
        "schema_version": 1,
        "source": {"name": "Test"},
        "nuclides": [
            {
                "name": "A",
                "atomic_number": 10,
                "mass_number": 20,
                "half_life_s": 100.0,
                "half_life_uncertainty_s": uncertainty,
                "decay_energy_mev": 0.0,
                "branches": [
                    {
                        "daughter": "B",
                        "fraction": 1.0,
                        "mode": "beta_minus",
                    }
                ],
            },
            {
                "name": "B",
                "atomic_number": 11,
                "mass_number": 20,
                "half_life_s": None,
                "decay_energy_mev": 0.0,
                "branches": [],
            },
        ],
    }


def load_document(tmp_path, document):
    path = tmp_path / "nuclides.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return load_nuclides(path)


@pytest.mark.parametrize("uncertainty", [0.0, 0.5, 50.0])
def test_valid_uncertainty_is_accepted(tmp_path, uncertainty):
    catalog = load_document(
        tmp_path,
        make_document(uncertainty),
    )

    assert catalog["A"]["half_life_uncertainty_s"] == uncertainty


@pytest.mark.parametrize(
    "uncertainty",
    [-1.0, float("inf"), float("nan"), True, "0.5", 100.0],
)
def test_invalid_uncertainty_is_rejected(tmp_path, uncertainty):
    with pytest.raises(ValueError):
        load_document(tmp_path, make_document(uncertainty))


def test_stable_nuclide_cannot_have_half_life_uncertainty(tmp_path):
    document = make_document(None)
    document["nuclides"][1]["half_life_uncertainty_s"] = 0.1

    with pytest.raises(ValueError):
        load_document(tmp_path, document)


def test_uncertainty_is_optional_for_legacy_catalogs(tmp_path):
    document = make_document(None)
    del document["nuclides"][0]["half_life_uncertainty_s"]

    catalog = load_document(tmp_path, document)

    assert "A" in catalog
