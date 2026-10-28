from nuclear_sim.telemetry.models import TelemetryReading
from nuclear_sim.telemetry.collector import TelemetryCollector
from nuclear_sim.plant.simulation import PlantState
from nuclear_sim.plant.simulation import PlantSimulation
from nuclear_sim.thermal.thermal_model import ThermalModel
from nuclear_sim.plant.simulation import Reactor
from nuclear_sim.telemetry.simulation_recorder import SimulationRecorder
from nuclear_sim.telemetry.history import HistoricalService
from nuclear_sim.safety.incident import Incident
from nuclear_sim.safety.system import SafetySystem
from nuclear_sim.safety.system import SafetyLimit
from nuclear_sim.plant.safety_integration import SafetyIntegration
from nuclear_sim.thermal.power_cycle import PowerCycle
from nuclear_sim.thermal.coolant import Coolant
from nuclear_sim.thermal.heat_transfer import HeatTransferModel
from nuclear_sim.thermal.steam_generator import SteamGenerator
from nuclear_sim.thermal.turbine import Turbine
from nuclear_sim.thermal.generator import Generator
import pytest

def create_power_cycle():
    return PowerCycle(
        coolant=Coolant(
            mass_flow_kg_s=1000.0,
            inlet_temperature_k=573.15,
            pressure_mpa=15.5,
        ),
        heat_transfer=HeatTransferModel(),
        steam_generator=SteamGenerator(),
        turbine=Turbine(),
        generator=Generator(),
    )

class FailingSimulation:
    def __init__(self):
        self._state = None
        self.reactor = Reactor(rated_power_mw=3000)

    def state(self):
        return self.reactor.state()

    def step(
        self,
        dt_s,
        heat_removed_mw,
        external_reactivity=None,
    ):
        raise RuntimeError("Fallo simulado")
    

def test_telemetry_reading_creation():
    reading = TelemetryReading(
        timestamp_s=10.5,
        variable="reactor_power",
        value=2400.0,
        unit="MW",
    )

    assert reading.timestamp_s == 10.5
    assert reading.variable == "reactor_power"
    assert reading.value == 2400.0
    assert reading.unit == "MW"


def test_telemetry_reading_is_immutable():
    reading = TelemetryReading(
        timestamp_s=10.5,
        variable="reactor_power",
        value=2400.0,
        unit="MW",
    )

    try:
        reading.value = 2500.0
        assert False, "TelemetryReading debería ser inmutable"
    except AttributeError:
        pass

def test_telemetry_collector_collects_plant_state():
    state = PlantState(
        time_s=10.0,
        power_mw=2400.0,
        temperature_k=600.0,
        reactor_status="running",
        electrical_power_mw=900.0,
        auxiliary_power_mw=50.0,
        net_electrical_power_mw=850.0,
    )

    collector = TelemetryCollector()

    readings = collector.collect(state)

    assert len(readings) == 20
    assert all(reading.timestamp_s == 10.0 for reading in readings)


def test_telemetry_collector_contains_reactor_power():
    state = PlantState(
        time_s=5.0,
        power_mw=2400.0,
        temperature_k=600.0,
        reactor_status="running",
        electrical_power_mw=900.0,
        auxiliary_power_mw=50.0,
        net_electrical_power_mw=850.0,
    )

    collector = TelemetryCollector()

    readings = collector.collect(state)

    reactor_power = next(
        reading
        for reading in readings
        if reading.variable == "reactor_power"
    )

    assert reactor_power.value == 2400.0
    assert reactor_power.unit == "MW"

def test_simulation_generates_telemetry():
    reactor = Reactor(rated_power_mw=3000)
    telemetry = TelemetryCollector()

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
        telemetry_collector=telemetry,
    )

    state = simulation.step(
        dt_s=0.1,
        heat_removed_mw=0.0,
    )

    readings = telemetry.collect(state)

    assert len(readings) == 20
    assert all(isinstance(reading, TelemetryReading) for reading in readings)

class FakeRepository:
    def __init__(self):
        self.created_runs = []
        self.saved_readings = []
        self.saved_incidents= []
        self.finished_runs = []

    def create_run(
        self,
        initial_power_fraction,
        description=None,
    ):
        self.created_runs.append(
            {
                "initial_power_fraction": initial_power_fraction,
                "description": description,
            }
        )

        return 123

    def save_readings(self, run_id, readings):
        self.saved_readings.append(
            {
                "run_id": run_id,
                "readings": readings,
            }
        )

    def save_incident(self, run_id, incident):
        self.saved_incidents.append(
            {
                "run_id": run_id,
                "incident": incident,
            }
        )

    def finish_run(self, run_id, status="completed"):
        self.finished_runs.append(
            {
                "run_id": run_id,
                "status": status,
            }
        )


def test_simulation_recorder_creates_run():
    reactor = Reactor(rated_power_mw=3000)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
    )

    repository = FakeRepository()

    recorder = SimulationRecorder(
        simulation=simulation,
        repository=repository,
    )

    run_id = recorder.start_run(
        description="Prueba de recorder",
    )

    assert run_id == 123
    assert len(repository.created_runs) == 1
    assert repository.created_runs[0]["description"] == (
        "Prueba de recorder"
    )


def test_simulation_recorder_saves_telemetry():
    reactor = Reactor(rated_power_mw=3000)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
    )

    repository = FakeRepository()

    recorder = SimulationRecorder(
        simulation=simulation,
        repository=repository,
    )

    recorder.start_run()

    state = recorder.step(
        dt_s=0.1,
        heat_removed_mw=0.0,
    )

    assert state.time_s == 0.1
    assert len(repository.saved_readings) == 1
    assert repository.saved_readings[0]["run_id"] == 123
    assert len(repository.saved_readings[0]["readings"]) == 20


def test_simulation_recorder_finishes_run():
    reactor = Reactor(rated_power_mw=3000)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
    )

    repository = FakeRepository()

    recorder = SimulationRecorder(
        simulation=simulation,
        repository=repository,
    )

    recorder.start_run()

    recorder.finish_run()

    assert len(repository.finished_runs) == 1
    assert repository.finished_runs[0]["run_id"] == 123
    assert repository.finished_runs[0]["status"] == "completed"

def test_simulation_recorder_marks_failed_run():
    reactor = Reactor(rated_power_mw=3000)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
    )

    repository = FakeRepository()

    recorder = SimulationRecorder(
        simulation=simulation,
        repository=repository,
    )

    recorder.start_run()

    recorder.finish_run(status="failed")

    assert len(repository.finished_runs) == 1
    assert repository.finished_runs[0]["run_id"] == 123
    assert repository.finished_runs[0]["status"] == "failed"


def test_simulation_recorder_requires_active_run():
    reactor = Reactor(rated_power_mw=3000)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
    )

    repository = FakeRepository()

    recorder = SimulationRecorder(
        simulation=simulation,
        repository=repository,
    )

    with pytest.raises(RuntimeError):
        recorder.step(
            dt_s=0.1,
            heat_removed_mw=0.0,
        )

def test_simulation_recorder_runs_complete_simulation():
    reactor = Reactor(rated_power_mw=3000)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
    )

    repository = FakeRepository()

    recorder = SimulationRecorder(
        simulation=simulation,
        repository=repository,
    )

    recorder.run(
        steps=3,
        dt_s=0.1,
        heat_removed_mw=0.0,
    )

    assert len(repository.created_runs) == 1
    assert len(repository.saved_readings) == 3
    assert len(repository.finished_runs) == 1

    assert repository.finished_runs[0]["status"] == "completed"


def test_simulation_recorder_marks_run_failed_on_error():
    simulation = FailingSimulation()
    repository = FakeRepository()

    recorder = SimulationRecorder(
        simulation=simulation,
        repository=repository,
    )

    with pytest.raises(RuntimeError, match="Fallo simulado"):
        recorder.run(
            steps=3,
            dt_s=0.1,
            heat_removed_mw=0.0,
        )

    assert len(repository.created_runs) == 1
    assert len(repository.finished_runs) == 1

    assert repository.finished_runs[0]["status"] == "failed"

class FakeHistoryRepository:
    def __init__(self):
        self.runs = [
            {
                "id": 1,
                "started_at": "2026-10-24 10:00:00",
                "ended_at": "2026-10-24 10:05:00",
                "description": "Simulación nominal",
                "initial_power_fraction": 0.8,
                "status": "completed",
            },
            {
                "id": 2,
                "started_at": "2026-10-24 11:00:00",
                "ended_at": None,
                "description": "Simulación en curso",
                "initial_power_fraction": 0.5,
                "status": "running",
            },
        ]

        self.readings = {
            1: [
                TelemetryReading(
                    timestamp_s=0.1,
                    variable="reactor_power",
                    value=2400.0,
                    unit="MW",
                ),
                TelemetryReading(
                    timestamp_s=0.2,
                    variable="reactor_power",
                    value=2410.0,
                    unit="MW",
                ),
            ]
        }
        self.incidents = {
            1: [
                Incident(
                    timestamp_s=1.5,
                    name="Core Temperature",
                    severity="warning",
                    message="Temperatura del núcleo elevada.",
                    source="SafetyIntegration",
                    status="open",
                )
            ]
        }

    def get_runs(self):
        return self.runs

    def get_readings(self, run_id, variable=None):
        readings = self.readings.get(run_id, [])

        if variable is None:
            return readings

        return [
            reading
            for reading in readings
            if reading.variable == variable
        ]

    def get_incidents(self, run_id):
        return self.incidents.get(run_id, [])
    
def test_historical_service_returns_runs():
    repository = FakeHistoryRepository()

    service = HistoricalService(repository)

    runs = service.get_runs()

    assert len(runs) == 2
    assert runs[0]["id"] == 1
    assert runs[0]["status"] == "completed"


def test_historical_service_returns_variable_history():
    repository = FakeHistoryRepository()

    service = HistoricalService(repository)

    readings = service.get_variable_history(
        run_id=1,
        variable="reactor_power",
    )

    assert len(readings) == 2
    assert readings[0].value == pytest.approx(2400.0)
    assert readings[1].value == pytest.approx(2410.0)


def test_historical_service_returns_empty_history_for_unknown_run():
    repository = FakeHistoryRepository()

    service = HistoricalService(repository)

    readings = service.get_variable_history(
        run_id=999,
        variable="reactor_power",
    )

    assert readings == []

def test_simulation_recorder_finish_clears_active_run():
    reactor = Reactor(rated_power_mw=3000)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
    )

    repository = FakeRepository()

    recorder = SimulationRecorder(
        simulation=simulation,
        repository=repository,
    )

    recorder.start_run()
    recorder.finish_run()

    assert recorder.run_id is None

def test_simulation_recorder_rejects_second_active_run():
    reactor = Reactor(rated_power_mw=3000)

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=ThermalModel(),
    )

    repository = FakeRepository()

    recorder = SimulationRecorder(
        simulation=simulation,
        repository=repository,
    )

    recorder.start_run()

    with pytest.raises(RuntimeError):
        recorder.start_run()

def test_historical_service_returns_incidents():
    repository = FakeHistoryRepository()

    service = HistoricalService(repository)

    incidents = service.get_incidents(
        run_id=1,
    )

    assert len(incidents) == 1

    incident = incidents[0]

    assert incident.timestamp_s == pytest.approx(1.5)
    assert incident.name == "Core Temperature"
    assert incident.severity == "warning"
    assert incident.message == "Temperatura del núcleo elevada."
    assert incident.source == "SafetyIntegration"
    assert incident.status == "open"

def test_simulation_recorder_persists_incident():
    reactor = Reactor(rated_power_mw=3000)
    thermal_model = ThermalModel()
    power_cycle = create_power_cycle()

    safety = SafetySystem()

    safety.add_limit(
        SafetyLimit(
            name="Primary Pressure",
            warning=15.0,
            critical=16.0,
        )
    )

    safety_integration = SafetyIntegration(
        reactor=reactor,
        safety_system=safety,
    )

    simulation = PlantSimulation(
        reactor=reactor,
        thermal_model=thermal_model,
        power_cycle=power_cycle,
        safety_integration=safety_integration,
    )

    repository = FakeRepository()

    recorder = SimulationRecorder(
        simulation=simulation,
        repository=repository,
    )

    recorder.start_run()

    recorder.step(
        dt_s=1.0,
        heat_removed_mw=0.0,
    )

    assert len(repository.saved_incidents) == 1

    saved = repository.saved_incidents[0]

    assert saved["run_id"] == 123
    assert saved["incident"].name == "Primary Pressure"
    assert saved["incident"].severity == "warning"
    assert saved["incident"].status == "open"