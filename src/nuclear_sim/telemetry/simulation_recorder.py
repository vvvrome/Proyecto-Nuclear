from nuclear_sim.plant.simulation import PlantSimulation
from nuclear_sim.database.repository import MySQLRepository
from .collector import TelemetryCollector
from nuclear_sim.reactor.results import OpenMCResult
from pathlib import Path
from nuclear_sim.reactor.runner import run_openmc

class SimulationRecorder:
    """Ejecuta una simulación y persiste su telemetría en MySQL."""

    def __init__(
        self,
        simulation: PlantSimulation,
        repository: MySQLRepository,
        collector: TelemetryCollector | None = None,
    ) -> None:
        self.simulation = simulation
        self.repository = repository
        self.collector = collector or TelemetryCollector()
        self.run_id: int | None = None
        self.last_run_id: int | None = None
        self._saved_incidents: set[tuple[str, float]] = set()
        
    def start_run(
        self,
        description: str | None = None,
    ) -> int:
        """Crea una nueva ejecución en la base de datos."""

        if self.run_id is not None:
            raise RuntimeError("Ya hay una ejecucion activa.")

        initial_power_fraction = (
            self.simulation.state().power_mw
            / self.simulation.reactor.rated_power_mw
        )

        self._saved_incidents.clear()

        self.run_id = self.repository.create_run(
            initial_power_fraction=initial_power_fraction,
            description=description,
        )

        self.last_run_id = self.run_id
        

        return self.run_id

    def save_openmc_result(
        self,
        result: OpenMCResult,
    ) -> int:
        """Guarda el resultado OpenMC de la ejecución actual."""

        if self.run_id is None:
            raise RuntimeError(
                "La ejecución no ha sido iniciada. "
                "Llama a start_run() antes de guardar resultados OpenMC."
            )

        return self.repository.save_openmc_result(
            run_id=self.run_id,
            result=result,
        )

    def run_and_save_openmc(
        self,
        output_directory: str | Path,
    ) -> int:
        """Ejecuta OpenMC y guarda su resultado en la ejecución actual."""

        if self.run_id is None:
            raise RuntimeError(
                "La ejecución no ha sido iniciada. "
                "Llama a start_run() antes de ejecutar OpenMC."
            )

        result = run_openmc(output_directory)

        return self.save_openmc_result(result)

    def step(
        self,
        dt_s: float,
        heat_removed_mw: float,
        external_reactivity: float | None = None,
    ):
        """Ejecuta un paso y guarda su telemetría."""

        if self.run_id is None:
            raise RuntimeError(
                "La ejecución no ha sido iniciada. "
                "Llama a start_run() antes de ejecutar pasos."
            )

        state = self.simulation.step(
            dt_s=dt_s,
            heat_removed_mw=heat_removed_mw,
            external_reactivity=external_reactivity,
        )

        readings = self.collector.collect(state)

        self.repository.save_readings(
            run_id=self.run_id,
            readings=readings,
        )

        if self.simulation.safety_state is not None:
            for incident in self.simulation.safety_state.incidents:
                incident_key = (
                    incident.name,
                    incident.timestamp_s,
                )

                if incident.status == "open":
                    if incident_key in self._saved_incidents:
                        continue

                    self.repository.save_incident(
                        run_id=self.run_id,
                        incident=incident,
                    )

                    self._saved_incidents.add(incident_key)

                else:
                    self.repository.save_incident(
                        run_id=self.run_id,
                        incident=incident,
                    )

        return state

    def finish_run(
        self,
        status: str = "completed",
    ) -> None:
        """Finaliza la ejecución actual."""

        if self.run_id is None:
            raise RuntimeError(
                "No hay ninguna ejecución activa."
            )

        run_id = self.run_id

        self.repository.finish_run(
            run_id=run_id,
            status=status,
        )

        self.run_id = None

    def run(
        self,
        steps: int,
        dt_s: float,
        heat_removed_mw: float,
        external_reactivity: float | None = None,
    ) -> None:
        """Ejecuta una simulación completa y registra su resultado."""

        self.start_run()

        try:
            for _ in range(steps):
                self.step(
                    dt_s=dt_s,
                    heat_removed_mw=heat_removed_mw,
                    external_reactivity=external_reactivity,
                )

        except Exception:
            self.finish_run(status="failed")
            raise

        else:
            self.finish_run(status="completed")
