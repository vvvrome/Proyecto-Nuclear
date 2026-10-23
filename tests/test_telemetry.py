from nuclear_sim.telemetry.models import TelemetryReading
from nuclear_sim.telemetry.collector import TelemetryCollector
from nuclear_sim.plant.simulation import PlantState
from nuclear_sim.plant.simulation import PlantSimulation
from nuclear_sim.thermal.thermal_model import ThermalModel
from nuclear_sim.plant.simulation import Reactor
from nuclear_sim.telemetry.simulation_recorder import SimulationRecorder
import pytest


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