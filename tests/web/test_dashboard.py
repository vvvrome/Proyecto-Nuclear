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
