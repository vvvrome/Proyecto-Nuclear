from typing import TYPE_CHECKING

from .models import TelemetryReading

if TYPE_CHECKING:
    from nuclear_sim.plant.simulation import PlantState


class TelemetryCollector:
    """Convierte el estado de la planta en lecturas de telemetría."""

    def collect(self, state: "PlantState") -> list[TelemetryReading]:
        timestamp = state.time_s

        return [
            TelemetryReading(
                timestamp_s=timestamp,
                variable="reactor_power",
                value=state.power_mw,
                unit="MW",
            ),
            TelemetryReading(
                timestamp_s=timestamp,
                variable="reactor_temperature",
                value=state.temperature_k,
                unit="K",
            ),
            TelemetryReading(
                timestamp_s=timestamp,
                variable="electrical_power",
                value=state.electrical_power_mw,
                unit="MW",
            ),
            TelemetryReading(
                timestamp_s=timestamp,
                variable="auxiliary_power",
                value=state.auxiliary_power_mw,
                unit="MW",
            ),
            TelemetryReading(
                timestamp_s=timestamp,
                variable="net_electrical_power",
                value=state.net_electrical_power_mw,
                unit="MW",
            ),
            TelemetryReading(
                timestamp_s=timestamp,
                variable="external_reactivity",
                value=state.external_reactivity,
                unit="delta_k_over_k",
            ),
            TelemetryReading(
                timestamp_s=timestamp,
                variable="temperature_reactivity",
                value=state.temperature_reactivity,
                unit="delta_k_over_k",
            ),
            TelemetryReading(
                timestamp_s=timestamp,
                variable="total_reactivity",
                value=state.total_reactivity,
                unit="delta_k_over_k",
            ),
            TelemetryReading(
                timestamp_s=timestamp,
                variable="neutron_population",
                value=state.neutron_population,
                unit="fraction",
            ),
            TelemetryReading(
                timestamp_s=timestamp,
                variable="transferred_power",
                value=state.transferred_power_mw,
                unit="MW",
            ),
            TelemetryReading(
                timestamp_s=timestamp,
                variable="lost_thermal_power",
                value=state.lost_thermal_power_mw,
                unit="MW",
            ),
            TelemetryReading(
                timestamp_s=timestamp,
                variable="useful_thermal_power",
                value=state.useful_thermal_power_mw,
                unit="MW",
            ),
            TelemetryReading(
                timestamp_s=timestamp,
                variable="coolant_outlet_temperature",
                value=state.coolant_outlet_temperature_k,
                unit="K",
            ),
            TelemetryReading(
                timestamp_s=timestamp,
                variable="steam_power",
                value=state.steam_power_mw,
                unit="MW",
            ),
            TelemetryReading(
                timestamp_s=timestamp,
                variable="mechanical_power",
                value=state.mechanical_power_mw,
                unit="MW",
            ),
            TelemetryReading(
                timestamp_s=timestamp,
                variable="turbine_speed",
                value=state.turbine_speed_rpm,
                unit="rpm",
            ),
            TelemetryReading(
                timestamp_s=timestamp,
                variable="rejected_heat",
                value=state.rejected_heat_mw,
                unit="MW",
            ),
            TelemetryReading(
                timestamp_s=timestamp,
                variable="condensed_heat",
                value=state.condensed_heat_mw,
                unit="MW",
            ),
            TelemetryReading(
                timestamp_s=timestamp,
                variable="condenser_outlet_temperature",
                value=state.condenser_outlet_temperature_k,
                unit="K",
            ),
            TelemetryReading(
                timestamp_s=timestamp,
                variable="pump_hydraulic_power",
                value=state.pump_hydraulic_power_mw,
                unit="MW",
            ),
        ]