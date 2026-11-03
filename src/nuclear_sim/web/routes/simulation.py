from flask import Blueprint, current_app, redirect, request, url_for


simulation_bp = Blueprint("simulation", __name__, url_prefix="/simulation")


@simulation_bp.post("/step")
def step():
    simulation = current_app.config["SIMULATION"]

    try:
        dt_s = float(request.form.get("dt_s", "0.1"))
        heat_removed_mw = float(request.form.get("heat_removed_mw", "0.0"))

        if dt_s <= 0 or heat_removed_mw < 0:
            raise ValueError

    except ValueError:
        return redirect(url_for("dashboard.index"))

    simulation.step(
        dt_s=dt_s,
        heat_removed_mw=heat_removed_mw,
    )

    return redirect(url_for("dashboard.index"))