from nuclear_sim.web.app import create_app


class FakeRepository:
    def __init__(self, connection):
        self.connection = connection

    def get_latest_openmc_result(self):
        return {
            "id": 1,
            "run_id": 125,
            "statepoint_path": "data/openmc/integration_run/statepoint.50.h5",
            "keff": 1.309444,
            "keff_std_dev": 0.004918,
            "batches": 50,
            "particles": 1000,
            "created_at": None,
        }
    def get_openmc_reference_points(self):
        return [
            {
                "id": 52,
                "run_id": 332,
                "keff": 1.2964897814756546,
                "keff_std_dev": 0.00477025113307639,
                "batches": 50,
                "particles": 1000,
                "fuel_temperature_K": 900.0,
                "moderator_temperature_K": 573.0,
                "u235_enrichment": 3.5,
            },
            {
                "id": 53,
                "run_id": 333,
                "keff": 1.3094440337578979,
                "keff_std_dev": 0.004917954181157431,
                "batches": 50,
                "particles": 1000,
                "fuel_temperature_K": 900.0,
                "moderator_temperature_K": 573.0,
                "u235_enrichment": 4.0,
            },
            {
                "id": 54,
                "run_id": 334,
                "keff": 1.3412139507633685,
                "keff_std_dev": 0.00468682205004236,
                "batches": 50,
                "particles": 1000,
                "fuel_temperature_K": 900.0,
                "moderator_temperature_K": 573.0,
                "u235_enrichment": 4.5,
            },
        ]

def test_dashboard_displays_latest_openmc_result(monkeypatch):
    monkeypatch.setattr(
        "nuclear_sim.web.app.create_connection",
        lambda: object(),
    )
    monkeypatch.setattr(
        "nuclear_sim.web.app.MySQLRepository",
        FakeRepository,
    )

    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200

    page = response.get_data(as_text=True)

    assert "Resultados OpenMC" in page
    assert "1.309444" in page
    assert "0.004918" in page
    assert "50" in page
    assert "1000" in page
    assert "Run ID: 125" in page
    assert "statepoint.50.h5" in page
