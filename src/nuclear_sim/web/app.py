from flask import Flask
import os
from nuclear_sim.plant.reactor import Reactor
from nuclear_sim.plant.simulation import PlantSimulation
from nuclear_sim.thermal.thermal_model import ThermalModel
from nuclear_sim.web.routes.dashboard import dashboard_bp
from nuclear_sim.web.routes.simulation import simulation_bp
from nuclear_sim.plant.reactor_dynamics import ReactorDynamics
from nuclear_sim.telemetry.collector import TelemetryCollector
from nuclear_sim.web.routes.asir import asir_bp
from nuclear_sim.web.routes.tfg_asir import tfg_asir_bp
from nuclear_sim.web.routes.fisica import fisica_bp
from nuclear_sim.web.routes.fisica_asignatura import fisica_asignatura_bp
from nuclear_sim.web.routes.files import files_bp
from nuclear_sim.web.file_storage import list_files
from nuclear_sim.web.routes.asir_asignatura import asir_asignatura_bp
from nuclear_sim.web.routes.fisica_curso import fisica_curso_bp

def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get(
        "NUCLEAR_SIM_SECRET_KEY",
        "nuclear-simulation-development-key",
    )
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
    app.jinja_env.globals["list_files"] = list_files

    reactor = Reactor(rated_power_mw=3000)
    thermal_model = ThermalModel()

    dynamics = ReactorDynamics(
        rated_power_mw=3000,
        thermal_model=thermal_model,
        initial_power_fraction=1.0,
    )

    telemetry = TelemetryCollector()

    app.config["SIMULATION"] = PlantSimulation(
        reactor=reactor,
        thermal_model=thermal_model,
        reactor_dynamics=dynamics,
        telemetry_collector=telemetry,
    )

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(simulation_bp)
    app.register_blueprint(asir_bp)
    app.register_blueprint(tfg_asir_bp)
    app.register_blueprint(fisica_bp)
    app.register_blueprint(fisica_asignatura_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(asir_asignatura_bp)
    app.register_blueprint(fisica_curso_bp)

    return app