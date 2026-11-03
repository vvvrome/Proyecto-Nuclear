from flask import Flask

from nuclear_sim.plant.reactor import Reactor
from nuclear_sim.plant.simulation import PlantSimulation
from nuclear_sim.thermal.thermal_model import ThermalModel
from nuclear_sim.web.routes.dashboard import dashboard_bp
from nuclear_sim.web.routes.simulation import simulation_bp
from nuclear_sim.plant.reactor_dynamics import ReactorDynamics
from nuclear_sim.telemetry.collector import TelemetryCollector


def create_app() -> Flask:
    app = Flask(__name__)

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

    return app