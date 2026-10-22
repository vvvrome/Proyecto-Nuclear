
import json

import pytest

from nuclear_sim.nuclear.nuclide_data import load_nuclides


def make_document():
    return {
        "schema_version": 1,
        "source": {
            "name": "Test",
            "reference": "Referencia ficticia",
            "url": "https://example.org/data",
            "data_status": "Datos de prueba",
        },
        "nuclides": [
            {
                "name": "A",
                "atomic_number": 10,
                "mass_number": 20,
                "half_life_s": 10.0,
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



def test_missing_source_name_is_rejected(tmp_path):
    document = make_document()
    del document["source"]["name"]

    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ValueError):
        load_nuclides(path)


@pytest.mark.parametrize(
    "field",
    ["reference", "url", "data_status"],
)
def test_optional_source_metadata_can_be_missing(tmp_path, field):
    document = make_document()
    del document["source"][field]

    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(document), encoding="utf-8")

    catalog = load_nuclides(path)

    assert "A" in catalog
    assert "B" in catalog



@pytest.mark.parametrize("url", ["", "example.org/data", "ftp://example.org"])
def test_invalid_source_url_is_rejected(tmp_path, url):
    document = make_document()
    document["source"]["url"] = url

    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ValueError):
        load_nuclides(path)


def test_valid_source_metadata_is_accepted(tmp_path):
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(make_document()), encoding="utf-8")

    catalog = load_nuclides(path)

    assert "A" in catalog
    assert "B" in catalog
