from flask import Blueprint, current_app, render_template, request


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/")
def index() -> str:
    simulation = current_app.config["SIMULATION"]
    state = simulation.state()

    repository = current_app.config.get("REPOSITORY")
    openmc_result = None

    if repository is not None:
        openmc_result = repository.get_latest_openmc_result()

    actuator_states = (
        simulation.controller.actuator_states()
        if simulation.controller is not None
        else {}
    )

    return render_template(
        "dashboard.html",
        state=state,
        openmc_result=openmc_result,
        dt_s=request.args.get("dt_s", "0.1"),
        heat_removed_mw=request.args.get("heat_removed_mw", "3000.0"),
        external_reactivity=request.args.get("external_reactivity", "0.0"),
    actuator_states=actuator_states,
    )
