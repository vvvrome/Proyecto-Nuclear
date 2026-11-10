from mysql.connector import MySQLConnection

from nuclear_sim.telemetry.models import TelemetryReading
from nuclear_sim.safety.incident import Incident

class MySQLRepository:
    """Repositorio para persistir ejecuciones y telemetría de la planta."""

    def __init__(self, connection: MySQLConnection) -> None:
        self.connection = connection

    def create_run(
        self,
        initial_power_fraction: float,
        description: str | None = None,
    ) -> int:
        """Crea una ejecución y devuelve su identificador."""

        cursor = self.connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO simulation_runs (
                    initial_power_fraction,
                    description
                )
                VALUES (%s, %s)
                """,
                (initial_power_fraction, description),
            )

            self.connection.commit()

            return cursor.lastrowid
        except Exception:
            self.connection.rollback()
            raise

        finally:
            cursor.close()

    def finish_run(self, run_id: int, status: str = "completed") -> None:
        """Finaliza una ejecución."""

        cursor = self.connection.cursor()

        try:
            cursor.execute(
                """
                UPDATE simulation_runs
                SET ended_at = CURRENT_TIMESTAMP,
                    status = %s
                WHERE id = %s
                """,
                (status, run_id),
            )

            self.connection.commit()

        except Exception:
            self.connection.rollback()
            raise
        
        finally:
            cursor.close()
    def save_openmc_result(
        self,
        run_id: int,
        result,
    ) -> int:
        """Guarda el resultado principal de una simulación OpenMC."""

        cursor = self.connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO openmc_results (
                    run_id,
                    statepoint_path,
                    keff,
                    keff_std_dev,
                    batches,
                    particles
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    run_id,
                    str(result.statepoint_path),
                    result.keff,
                    result.keff_std_dev,
                    result.batches,
                    result.particles,
                ),
            )

            self.connection.commit()

            return cursor.lastrowid

        except Exception:
            self.connection.rollback()
            raise

        finally:
            cursor.close()
    def save_reading(
        self,
        run_id: int,
        reading: TelemetryReading,
    ) -> int:
        """Guarda una lectura de telemetría."""

        cursor = self.connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO telemetry_readings (
                    run_id,
                    timestamp_s,
                    variable,
                    value,
                    unit
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    run_id,
                    reading.timestamp_s,
                    reading.variable,
                    reading.value,
                    reading.unit,
                ),
            )

            self.connection.commit()

            return cursor.lastrowid

        except Exception:
            self.connection.rollback()
            raise
        
        finally:
            cursor.close()

    def save_readings(
        self,
        run_id: int,
        readings: list[TelemetryReading],
    ) -> None:
        """Guarda varias lecturas de telemetría en una sola operación."""

        if not readings:
            return

        cursor = self.connection.cursor()

        try:
            cursor.executemany(
                """
                INSERT INTO telemetry_readings (
                    run_id,
                    timestamp_s,
                    variable,
                    value,
                    unit
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                [
                    (
                        run_id,
                        reading.timestamp_s,
                        reading.variable,
                        reading.value,
                        reading.unit,
                    )
                    for reading in readings
                ],
            )

            self.connection.commit()

        except Exception:
            self.connection.rollback()
            raise

        finally:
            cursor.close()

    def save_incident(
        self,
        run_id: int,
        incident: Incident,
    ) -> int:
        """Guarda un incidente asociado a una ejecución."""

        cursor = self.connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO incidents (
                    run_id,
                    timestamp_s,
                    name,
                    severity,
                    message,
                    source,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    run_id,
                    incident.timestamp_s,
                    incident.name,
                    incident.severity,
                    incident.message,
                    incident.source,
                    incident.status,
                ),
            )

            self.connection.commit()

            return cursor.lastrowid

        except Exception:
            self.connection.rollback()
            raise
        
        finally:
            cursor.close()

    def get_incidents(
        self,
        run_id: int,
    ) -> list[Incident]:
        """Obtiene los incidentes de una ejecución."""

        cursor = self.connection.cursor()

        try:
            cursor.execute(
                """
                SELECT
                    timestamp_s,
                    name,
                    severity,
                    message,
                    source,
                    status
                FROM incidents
                WHERE run_id = %s
                ORDER BY timestamp_s, id
                """,
                (run_id,),
            )

            return [
                Incident(
                    timestamp_s=row[0],
                    name=row[1],
                    severity=row[2],
                    message=row[3],
                    source=row[4],
                    status=row[5],
                )
                for row in cursor.fetchall()
            ]

        finally:
            cursor.close()

    def get_readings(
        self,
        run_id: int,
        variable: str | None = None,
    ) -> list[TelemetryReading]:
        """Obtiene las lecturas de una ejecución."""

        cursor = self.connection.cursor()

        try:
            if variable is None:
                cursor.execute(
                    """
                    SELECT timestamp_s, variable, value, unit
                    FROM telemetry_readings
                    WHERE run_id = %s
                    ORDER BY timestamp_s, id
                    """,
                    (run_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT timestamp_s, variable, value, unit
                    FROM telemetry_readings
                    WHERE run_id = %s
                      AND variable = %s
                    ORDER BY timestamp_s, id
                    """,
                    (run_id, variable),
                )

            return [
                TelemetryReading(
                    timestamp_s=row[0],
                    variable=row[1],
                    value=row[2],
                    unit=row[3],
                )
                for row in cursor.fetchall()
            ]
        finally:
            cursor.close()

    def get_runs(self) -> list[dict]:
        """Obtiene todas las ejecuciones almacenadas."""

        cursor = self.connection.cursor()

        try:
            cursor.execute(
                """
                SELECT
                    id,
                    started_at,
                    ended_at,
                    description,
                    initial_power_fraction,
                    status
                FROM simulation_runs
                ORDER BY started_at DESC, id DESC
                """
            )

            rows = cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "started_at": row[1],
                    "ended_at": row[2],
                    "description": row[3],
                    "initial_power_fraction": row[4],
                    "status": row[5],
                }
                for row in rows
            ]

        finally:
            cursor.close()
