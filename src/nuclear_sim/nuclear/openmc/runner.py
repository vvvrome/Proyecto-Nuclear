from pathlib import Path
import subprocess

from .result import OpenMCResult


class OpenMCRunner:
    """Ejecuta una simulación OpenMC en un proceso separado."""

    def __init__(
        self,
        python_executable: str,
        model_script: str,
    ) -> None:
        self.python_executable = Path(python_executable)
        self.model_script = Path(model_script)

    def run(self) -> OpenMCResult:
        """Ejecuta OpenMC y devuelve el resultado de la simulación."""

        subprocess.run(
            [
                str(self.python_executable),
                str(self.model_script),
            ],
            check=True,
            cwd=self.model_script.parent,
        )

        statepoints = sorted(
            self.model_script.parent.glob("statepoint.*.h5")
        )

        if not statepoints:
            raise FileNotFoundError(
                "OpenMC no ha generado ningún statepoint."
            )

        statepoint_path = statepoints[-1]

        result_script = self.model_script.parent / "_read_statepoint.py"

        result_script.write_text(
            """
import openmc
import sys

statepoint_path = sys.argv[1]

with openmc.StatePoint(statepoint_path) as statepoint:
    print(statepoint.keff.nominal_value)
    print(statepoint.keff.std_dev)
""",
            encoding="utf-8",
        )

        try:
            result = subprocess.run(
                [
                    str(self.python_executable),
                    str(result_script),
                    str(statepoint_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        finally:
            result_script.unlink(missing_ok=True)

        lines = result.stdout.strip().splitlines()

        if len(lines) != 2:
            raise RuntimeError(
                "No se pudo obtener el resultado de OpenMC."
            )

        keff = float(lines[0])
        keff_uncertainty = float(lines[1])

        return OpenMCResult(
            keff=keff,
            keff_uncertainty=keff_uncertainty,
            statepoint_path=str(statepoint_path),
        )
