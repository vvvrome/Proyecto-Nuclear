import pytest
import os

from nuclear_sim.database.connection import create_connection
from nuclear_sim.database.repository import MySQLRepository
from nuclear_sim.database.repository import TelemetryReading
from nuclear_sim.thermal.thermal_model import ThermalModel
from nuclear_sim.plant.reactor import Reactor
from nuclear_sim.plant.simulation import PlantSimulation
from nuclear_sim.telemetry.simulation_recorder import SimulationRecorder
from nuclear_sim.safety.incident import Incident
from nuclear_sim.plant.safety_integration import SafetyIntegration
from nuclear_sim.safety.limits import SafetyLimit
from nuclear_sim.safety.system import SafetySystem
from nuclear_sim.thermal.power_cycle import PowerCycle
from nuclear_sim.thermal.coolant import Coolant
from nuclear_sim.thermal.heat_transfer import HeatTransferModel
from nuclear_sim.thermal.steam_generator import SteamGenerator
from nuclear_sim.thermal.turbine import Turbine
from nuclear_sim.thermal.generator import Generator
from nuclear_sim.reactor.results import OpenMCResult

class FailingSimulation:
    def __init__(self):
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


def test_create_connection_function_exists():
    assert callable(create_connection)


def test_repository_can_be_created():
    repository = MySQLRepository(connection=None)

    assert repository.connection is None


def test_repository_save_readings_accepts_empty_list():
    repository = MySQLRepository(connection=None)

    repository.save_readings(
        run_id=1,
        readings=[],
    )

@pytest.mark.integration
def test_mysql_repository_persists_telemetry():
    connection = create_connection()

    try:
        repository = MySQLRepository(connection)

        run_id = repository.create_run(
            initial_power_fraction=0.8,
            description="Test de integración de telemetría",
        )

        reading = TelemetryReading(
            timestamp_s=1.5,
            variable="reactor_power",
            value=2400.0,
            unit="MW",
        )

        repository.save_reading(
            run_id=run_id,
            reading=reading,
        )

        readings = repository.get_readings(
            run_id=run_id,
            variable="reactor_power",
        )

        assert len(readings) == 1
        assert readings[0].timestamp_s == pytest.approx(1.5)
        assert readings[0].variable == "reactor_power"
        assert readings[0].value == pytest.approx(2400.0)
        assert readings[0].unit == "MW"

        repository.finish_run(run_id)

    finally:
        connection.close()

@pytest.mark.integration
def test_simulation_recorder_persists_real_simulation():
    connection = create_connection()

    run_id = None

    try:
        repository = MySQLRepository(connection)

        reactor = Reactor(rated_power_mw=3000)

        power_cycle = PowerCycle(
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
            thermal_model=ThermalModel(),
            power_cycle=power_cycle,
            safety_integration=safety_integration,
        )

        recorder = SimulationRecorder(
            simulation=simulation,
            repository=repository,
        )

        run_id = recorder.start_run(
            description="Prueba de integración de simulación",
        )

        for _ in range(3):
            recorder.step(
                dt_s=0.1,
                heat_removed_mw=0.0,
            )

        recorder.finish_run()

        readings = repository.get_readings(
            run_id=run_id,
        )

        incidents = repository.get_incidents(
            run_id=run_id,
        )

        assert len(incidents) == 1
        assert incidents[0].name == "Primary Pressure"
        assert incidents[0].severity == "warning"
        assert incidents[0].status == "open"

        assert len(readings) == 60

        assert readings[0].timestamp_s == pytest.approx(0.1)
        assert readings[-1].timestamp_s == pytest.approx(0.3)

        variables = {
            reading.variable
            for reading in readings
        }

        assert "reactor_power" in variables
        assert "reactor_temperature" in variables
        assert "total_reactivity" in variables
        assert "neutron_population" in variables

    finally:
        if run_id is not None:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    "DELETE FROM simulation_runs WHERE id = %s",
                    (run_id,),
                )
                connection.commit()
            finally:
                cursor.close()

        connection.close()

@pytest.mark.integration
def test_simulation_recorder_persists_completed_run():
    connection = create_connection()
    run_id = None

    try:
        repository = MySQLRepository(connection)

        simulation = PlantSimulation(
            reactor=Reactor(rated_power_mw=3000),
            thermal_model=ThermalModel(),
        )

        recorder = SimulationRecorder(
            simulation=simulation,
            repository=repository,
        )

        recorder.start_run(
            description="Prueba de ejecución completa",
        )

        run_id = recorder.run_id

        for _ in range(3):
            recorder.step(
                dt_s=0.1,
                heat_removed_mw=0.0,
            )

        recorder.finish_run()

        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                SELECT status, ended_at
                FROM simulation_runs
                WHERE id = %s
                """,
                (run_id,),
            )

            row = cursor.fetchone()

        finally:
            cursor.close()

        assert row is not None
        assert row[0] == "completed"
        assert row[1] is not None

    finally:
        if run_id is not None:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    "DELETE FROM simulation_runs WHERE id = %s",
                    (run_id,),
                )
                connection.commit()
            finally:
                cursor.close()

        connection.close()

@pytest.mark.integration
def test_simulation_recorder_persists_failed_run():
    connection = create_connection()
    run_id = None

    try:
        repository = MySQLRepository(connection)

        simulation = FailingSimulation()

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

        run_id = recorder.last_run_id

        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                SELECT status, ended_at
                FROM simulation_runs
                WHERE id = %s
                """,
                (run_id,),
            )

            row = cursor.fetchone()

        finally:
            cursor.close()

        assert row is not None
        assert row[0] == "failed"
        assert row[1] is not None

    finally:
        if run_id is not None:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    "DELETE FROM simulation_runs WHERE id = %s",
                    (run_id,),
                )
                connection.commit()
            finally:
                cursor.close()

        connection.close()

@pytest.mark.integration
def test_repository_returns_runs():
    connection = create_connection()
    run_id = None

    try:
        repository = MySQLRepository(connection)

        run_id = repository.create_run(
            initial_power_fraction=0.8,
            description="Prueba de consulta histórica",
        )

        runs = repository.get_runs()

        matching_runs = [
            run for run in runs
            if run["id"] == run_id
        ]

        assert len(matching_runs) == 1
        assert matching_runs[0]["initial_power_fraction"] == pytest.approx(0.8)
        assert matching_runs[0]["description"] == (
            "Prueba de consulta histórica"
        )
        assert matching_runs[0]["status"] == "running"

    finally:
        if run_id is not None:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    "DELETE FROM simulation_runs WHERE id = %s",
                    (run_id,),
                )
                connection.commit()
            finally:
                cursor.close()

        connection.close()

@pytest.mark.integration
def test_repository_persists_incident():
    connection = create_connection()
    run_id = None

    try:
        repository = MySQLRepository(connection)

        run_id = repository.create_run(
            initial_power_fraction=0.8,
            description="Prueba de persistencia de incidente",
        )

        incident = Incident(
            timestamp_s=1.5,
            name="Core Temperature",
            severity="critical",
            message="Temperatura del núcleo por encima del límite crítico.",
            source="SafetyIntegration",
            status="open",
        )

        incident_id = repository.save_incident(
            run_id=run_id,
            incident=incident,
        )

        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                SELECT
                    id,
                    run_id,
                    timestamp_s,
                    name,
                    severity,
                    message,
                    source,
                    status
                FROM incidents
                WHERE id = %s
                """,
                (incident_id,),
            )

            row = cursor.fetchone()

        finally:
            cursor.close()

        assert row is not None
        assert row[0] == incident_id
        assert row[1] == run_id
        assert row[2] == pytest.approx(1.5)
        assert row[3] == "Core Temperature"
        assert row[4] == "critical"
        assert row[5] == (
            "Temperatura del núcleo por encima del límite crítico."
        )
        assert row[6] == "SafetyIntegration"
        assert row[7] == "open"

    finally:
        if run_id is not None:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    "DELETE FROM simulation_runs WHERE id = %s",
                    (run_id,),
                )
                connection.commit()
            finally:
                cursor.close()

        connection.close()

@pytest.mark.integration
def test_repository_returns_incidents():
    connection = create_connection()
    run_id = None

    try:
        repository = MySQLRepository(connection)

        run_id = repository.create_run(
            initial_power_fraction=0.8,
            description="Prueba de consulta de incidentes",
        )

        incident = Incident(
            timestamp_s=2.5,
            name="Core Temperature",
            severity="warning",
            message="Temperatura del núcleo elevada.",
            source="SafetyIntegration",
            status="open",
        )

        repository.save_incident(
            run_id=run_id,
            incident=incident,
        )

        incidents = repository.get_incidents(
            run_id=run_id,
        )

        assert len(incidents) == 1

        result = incidents[0]

        assert result.timestamp_s == pytest.approx(2.5)
        assert result.name == "Core Temperature"
        assert result.severity == "warning"
        assert result.message == "Temperatura del núcleo elevada."
        assert result.source == "SafetyIntegration"
        assert result.status == "open"

    finally:
        if run_id is not None:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    "DELETE FROM simulation_runs WHERE id = %s",
                    (run_id,),
                )
                connection.commit()
            finally:
                cursor.close()

        connection.close()

def test_repository_rolls_back_when_create_run_fails():
    class FailingCursor:
        def execute(self, *args, **kwargs):
            raise RuntimeError("Fallo SQL simulado")

        def close(self):
            pass

    class FakeConnection:
        def __init__(self):
            self.rollback_called = False

        def cursor(self):
            return FailingCursor()

        def commit(self):
            pass

        def rollback(self):
            self.rollback_called = True

    connection = FakeConnection()
    repository = MySQLRepository(connection)

    with pytest.raises(RuntimeError, match="Fallo SQL simulado"):
        repository.create_run(
            initial_power_fraction=0.8,
            description="Test rollback",
        )

    assert connection.rollback_called is True

def test_repository_rolls_back_when_finish_run_fails():
    class FailingCursor:
        def execute(self, *args, **kwargs):
            raise RuntimeError("Fallo SQL simulado")

        def close(self):
            pass

    class FakeConnection:
        def __init__(self):
            self.rollback_called = False

        def cursor(self):
            return FailingCursor()

        def commit(self):
            pass

        def rollback(self):
            self.rollback_called = True

    connection = FakeConnection()
    repository = MySQLRepository(connection)

    with pytest.raises(RuntimeError, match="Fallo SQL simulado"):
        repository.finish_run(
            run_id=1,
            status="completed",
        )

    assert connection.rollback_called is True

def test_repository_rolls_back_when_save_reading_fails():
    class FailingCursor:
        def execute(self, *args, **kwargs):
            raise RuntimeError("Fallo SQL simulado")

        def close(self):
            pass

    class FakeConnection:
        def __init__(self):
            self.rollback_called = False

        def cursor(self):
            return FailingCursor()

        def commit(self):
            pass

        def rollback(self):
            self.rollback_called = True

    connection = FakeConnection()
    repository = MySQLRepository(connection)

    reading = TelemetryReading(
        timestamp_s=1.0,
        variable="reactor_power",
        value=2400.0,
        unit="MW",
    )

    with pytest.raises(RuntimeError, match="Fallo SQL simulado"):
        repository.save_reading(
            run_id=1,
            reading=reading,
        )

    assert connection.rollback_called is True

@pytest.mark.integration
def test_mysql_repository_persists_openmc_result():
    connection = create_connection()
    run_id = None

    try:
        repository = MySQLRepository(connection)

        run_id = repository.create_run(
            initial_power_fraction=1.0,
            description="Test de integración de resultados OpenMC",
        )

        result = OpenMCResult(
            statepoint_path="data/openmc/test_run/statepoint.50.h5",
            keff=1.309444033757898,
            keff_std_dev=0.004917954181157573,
            batches=50,
            particles=1000,
        )

        result_id = repository.save_openmc_result(
            run_id=run_id,
            result=result,
        )

        assert result_id is not None

        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                SELECT
                    run_id,
                    statepoint_path,
                    keff,
                    keff_std_dev,
                    batches,
                    particles
                FROM openmc_results
                WHERE id = %s
                """,
                (result_id,),
            )

            row = cursor.fetchone()

        finally:
            cursor.close()

        assert row is not None
        assert row[0] == run_id
        assert row[1] == "data/openmc/test_run/statepoint.50.h5"
        assert row[2] == pytest.approx(1.309444033757898)
        assert row[3] == pytest.approx(0.004917954181157573)
        assert row[4] == 50
        assert row[5] == 1000

    finally:
        if run_id is not None:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    "DELETE FROM simulation_runs WHERE id = %s",
                    (run_id,),
                )
                connection.commit()
            finally:
                cursor.close()

        connection.close()

def test_simulation_recorder_run_and_save_openmc(monkeypatch):
    class FakeRepository:
        def __init__(self):
            self.saved_result = None

        def save_openmc_result(self, run_id, result):
            self.saved_result = (run_id, result)
            return 123

    repository = FakeRepository()

    simulation = PlantSimulation(
        reactor=Reactor(rated_power_mw=3000),
        thermal_model=ThermalModel(),
    )

    recorder = SimulationRecorder(
        simulation=simulation,
        repository=repository,
    )

    recorder.run_id = 42

    expected_result = OpenMCResult(
        statepoint_path="data/openmc/test_run/statepoint.50.h5",
        keff=1.309444033757898,
        keff_std_dev=0.004917954181157573,
        batches=50,
        particles=1000,
    )

    def fake_run_openmc(output_directory):
        assert output_directory == "data/openmc/test_run"
        return expected_result

    monkeypatch.setattr(
        "nuclear_sim.telemetry.simulation_recorder.run_openmc",
        fake_run_openmc,
    )

    result_id = recorder.run_and_save_openmc(
        "data/openmc/test_run",
    )

    assert result_id == 123
    assert repository.saved_result is not None

    saved_run_id, saved_result = repository.saved_result

    assert saved_run_id == 42
    assert saved_result == expected_result
