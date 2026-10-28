from nuclear_sim.database.repository import MySQLRepository


class HistoricalService:
    """Servicio para consultar el histórico de simulaciones."""

    def __init__(self, repository: MySQLRepository) -> None:
        self.repository = repository

    def get_runs(self) -> list[dict]:
        """Obtiene todas las ejecuciones almacenadas."""
        return self.repository.get_runs()

    def get_variable_history(
        self,
        run_id: int,
        variable: str,
    ):
        """Obtiene el histórico de una variable de una ejecución."""
        return self.repository.get_readings(
            run_id=run_id,
            variable=variable,
        )

    def get_incidents(self, run_id: int):
        """Obtiene los incidentes de una ejecución."""
        return self.repository.get_incidents(
            run_id=run_id,
        )