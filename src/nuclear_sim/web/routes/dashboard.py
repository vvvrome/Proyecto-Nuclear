from flask import Blueprint, current_app, render_template


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/")
def index() -> str:
    simulation = current_app.config["SIMULATION"]
    state = simulation.state()

    return render_template(
        "dashboard.html",
        state=state,
    )