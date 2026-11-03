from nuclear_sim.web.app import create_app


def test_dashboard_returns_200():
    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200

def test_simulation_step_updates_state():
    app = create_app()
    client = app.test_client()

    response = client.post("/simulation/step")

    assert response.status_code == 302

    simulation = app.config["SIMULATION"]

    assert simulation.state().time_s > 0.0

def test_simulation_step_accepts_custom_dt():
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/simulation/step",
        data={"dt_s": "1.0"},
    )

    assert response.status_code == 302

    simulation = app.config["SIMULATION"]

    assert simulation.state().time_s == 1.0

def test_simulation_step_accepts_heat_removal():
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/simulation/step",
        data={
            "dt_s": "0.1",
            "heat_removed_mw": "10.0",
        },
    )

    assert response.status_code == 302

    simulation = app.config["SIMULATION"]

    assert simulation.state().time_s == 0.1