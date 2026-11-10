from flask import Blueprint, current_app, render_template


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/")
def index() -> str:
    simulation = current_app.config["SIMULATION"]
    state = simulation.state()

    repository = current_app.config.get("REPOSITORY")
    openmc_result = None

    if repository is not None:
        openmc_result = repository.get_latest_openmc_result()

    return render_template(
        "dashboard.html",
        state=state,
        openmc_result=openmc_result,
    )
