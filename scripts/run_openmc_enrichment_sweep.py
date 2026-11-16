from pathlib import Path

from nuclear_sim.reactor.materials import ReactorMaterialConfig
from nuclear_sim.reactor.runner import run_openmc
from nuclear_sim.reactor.simulation import ReactorSimulationConfig


BASE_OUTPUT = Path("data/openmc/parametric/enrichment")


def main() -> None:
    enrichments = [3.5, 4.0, 4.5]

    for enrichment in enrichments:
        output_directory = BASE_OUTPUT / f"u235_{enrichment:.1f}"

        material_config = ReactorMaterialConfig(
            enrichment_u235=enrichment,
            fuel_temperature=900.0,
            coolant_temperature=573.0,
            coolant_density=0.743,
            helium_density=0.0016,
            cladding_temperature=573.0,
        )

        simulation_config = ReactorSimulationConfig(
            materials=material_config,
        )

        print()
        print("=" * 60)
        print(f"Running U-235 enrichment = {enrichment:.1f}%")
        print(f"Output: {output_directory}")
        print("=" * 60)

        result = run_openmc(
            str(output_directory),
            config=simulation_config,
        )

        print()
        print("Result:")
        print(result)


if __name__ == "__main__":
    main()
