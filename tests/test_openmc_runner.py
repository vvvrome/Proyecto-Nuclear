import pytest

from nuclear_sim.nuclear.openmc.runner import OpenMCRunner
from nuclear_sim.nuclear.openmc.result import OpenMCResult


@pytest.mark.integration
def test_openmc_runner_returns_result(tmp_path):
    model_script = tmp_path / "model.py"

    model_script.write_text(
        """
import openmc

fuel = openmc.Material(name="Test Fuel")
fuel.set_density("g/cm3", 10.0)
fuel.add_nuclide("U235", 1.0)
fuel.add_nuclide("U238", 3.0)

materials = openmc.Materials([fuel])

sphere = openmc.Sphere(r=10.0, boundary_type="vacuum")
cell = openmc.Cell(fill=fuel, region=-sphere)

geometry = openmc.Geometry([cell])

settings = openmc.Settings()
settings.batches = 5
settings.inactive = 1
settings.particles = 1000

source = openmc.IndependentSource()
source.space = openmc.stats.Point((0.0, 0.0, 0.0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([1.0e6], [1.0])

settings.source = source

model = openmc.Model(
    geometry=geometry,
    materials=materials,
    settings=settings,
)

model.run()
""",
        encoding="utf-8",
    )

    runner = OpenMCRunner(
        python_executable="/home/vvvrome/miniforge3/envs/openmc-env/bin/python",
        model_script=str(model_script),
    )

    result = runner.run()

    assert isinstance(result, OpenMCResult)
    assert result.keff > 0
    assert result.keff_uncertainty > 0
    assert result.statepoint_path.endswith(".h5")
