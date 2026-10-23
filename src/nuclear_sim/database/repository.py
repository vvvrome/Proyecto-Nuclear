from mysql.connector import MySQLConnection

from nuclear_sim.telemetry.models import TelemetryReading


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