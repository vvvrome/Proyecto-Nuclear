import pytest
import os

from nuclear_sim.database.connection import create_connection
from nuclear_sim.database.repository import MySQLRepository
from nuclear_sim.database.repository import TelemetryReading
from nuclear_sim.thermal.thermal_model import ThermalModel
from nuclear_sim.plant.reactor import Reactor
from nuclear_sim.plant.simulation import PlantSimulation
from nuclear_sim.telemetry.simulation_recorder import SimulationRecorder

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

        simulation = PlantSimulation(
            reactor=Reactor(rated_power_mw=3000),
            thermal_model=ThermalModel(),
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