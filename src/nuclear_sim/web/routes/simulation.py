from flask import Blueprint, current_app, jsonify, redirect, request, url_for


simulation_bp = Blueprint("simulation", __name__, url_prefix="/simulation")


@simulation_bp.post("/step")
def step():
    simulation = current_app.config["SIMULATION"]

    try:
        dt_s = float(request.form.get("dt_s", "0.1"))
        heat_removed_mw = float(request.form.get("heat_removed_mw", "3000.0"))
        external_reactivity = float(
            request.form.get("external_reactivity", "0.0")
        )

        if (
            dt_s <= 0
            or heat_removed_mw < 0
            or not (-0.01 <= external_reactivity <= 0.01)
        ):
            raise ValueError

    except ValueError:
        return redirect(url_for("dashboard.index"))

    simulation.step(
        dt_s=dt_s,
        heat_removed_mw=heat_removed_mw,
        external_reactivity=external_reactivity,
    )

    return redirect(
        url_for(
            "dashboard.index",
            dt_s=dt_s,
            heat_removed_mw=heat_removed_mw,
            external_reactivity=external_reactivity,
        )
    )

@simulation_bp.post("/reset")
def reset():
    simulation = current_app.config["SIMULATION"]
    simulation.reset()

    return redirect(url_for("dashboard.index"))


@simulation_bp.get("/telemetry")
def telemetry():
    simulation = current_app.config["SIMULATION"]
    collector = simulation.telemetry_collector

    readings = collector.readings if collector is not None else []

    return jsonify(
        [
            {
                "timestamp_s": reading.timestamp_s,
                "variable": reading.variable,
                "value": reading.value,
                "unit": reading.unit,
            }
            for reading in readings
        ]
    )

@simulation_bp.get("/openmc/<int:run_id>")
def openmc_result(run_id: int):
    repository = current_app.config["REPOSITORY"]

    result = repository.get_openmc_result(run_id)

    if result is None:
        return jsonify({"error": "OpenMC result not found"}), 404

    return jsonify(result)
