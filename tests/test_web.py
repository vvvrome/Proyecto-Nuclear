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

def test_telemetry_endpoint_returns_readings():
    app = create_app()
    client = app.test_client()

    client.post(
        "/simulation/step",
        data={
            "dt_s": "0.1",
            "heat_removed_mw": "0.0",
        },
    )

    response = client.get("/simulation/telemetry")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 20
    assert data[0]["timestamp_s"] == 0.1

def test_asir_subject_returns_200():
    app = create_app()
    client = app.test_client()

    response = client.get("/asir/primero/m00377/")

    assert response.status_code == 200


def test_asir_unknown_subject_returns_404():
    app = create_app()
    client = app.test_client()

    response = client.get("/asir/primero/no-existe/")

    assert response.status_code == 404


def test_fisica_course_returns_200():
    app = create_app()
    client = app.test_client()

    response = client.get("/fisica/segundo/")

    assert response.status_code == 200


def test_fisica_all_courses_return_200():
    app = create_app()
    client = app.test_client()

    courses = [
        "primero",
        "segundo",
        "tercero",
        "cuarto",
    ]

    for course in courses:
        response = client.get(f"/fisica/{course}/")

        assert response.status_code == 200


def test_fisica_subject_returns_200():
    app = create_app()
    client = app.test_client()

    response = client.get(
        "/fisica/tercero/fisica-cuantica-i/"
    )

    assert response.status_code == 200


def test_fisica_unknown_course_returns_404():
    app = create_app()
    client = app.test_client()

    response = client.get("/fisica/quinto/")

    assert response.status_code == 404


def test_fisica_unknown_subject_returns_404():
    app = create_app()
    client = app.test_client()

    response = client.get(
        "/fisica/segundo/asignatura-inexistente/"
    )

    assert response.status_code == 404