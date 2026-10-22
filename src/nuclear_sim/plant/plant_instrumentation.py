from typing import TYPE_CHECKING

from nuclear_sim.instrumentation.sensor import Sensor
from nuclear_sim.instrumentation.actuator import Actuator
from nuclear_sim.instrumentation.system import InstrumentationSystem

if TYPE_CHECKING:
    from nuclear_sim.plant.simulation import PlantState


class PlantInstrumentation:
    """Instrumentación asociada al estado de la planta."""

    def __init__(self):
        self.system = InstrumentationSystem()

        self._create_sensors()
        self._create_actuators()

    def _create_sensors(self):
        # Reactor
        self.system.add_sensor(
            Sensor(
                name="reactor_power",
                unit="MW",
            )
        )

        self.system.add_sensor(
            Sensor(
                name="reactor_temperature",
                unit="K",
            )
        )

        self.system.add_sensor(
            Sensor(
                name="neutron_population",
                unit="normalized",
            )
        )

        self.system.add_sensor(
            Sensor(
                name="reactivity",
                unit="rho",
            )
        )

        # Thermal
        self.system.add_sensor(
            Sensor(
                name="transferred_power",
                unit="MW",
            )
        )

        self.system.add_sensor(
            Sensor(
                name="thermal_losses",
                unit="MW",
            )
        )

        self.system.add_sensor(
            Sensor(
                name="useful_thermal_power",
                unit="MW",
            )
        )

        self.system.add_sensor(
            Sensor(
                name="coolant_outlet_temperature",
                unit="K",
            )
        )

        # Steam / turbine
        self.system.add_sensor(
            Sensor(
                name="steam_power",
                unit="MW",
            )
        )

        self.system.add_sensor(
            Sensor(
                name="mechanical_power",
                unit="MW",
            )
        )

        self.system.add_sensor(
            Sensor(
                name="turbine_speed",
                unit="RPM",
            )
        )

        # Electrical
        self.system.add_sensor(
            Sensor(
                name="electrical_power",
                unit="MW",
            )
        )

        self.system.add_sensor(
            Sensor(
                name="net_electrical_power",
                unit="MW",
            )
        )

        # Condenser
        self.system.add_sensor(
            Sensor(
                name="rejected_heat",
                unit="MW",
            )
        )

        self.system.add_sensor(
            Sensor(
                name="condensed_heat",
                unit="MW",
            )
        )

        self.system.add_sensor(
            Sensor(
                name="condenser_outlet_temperature",
                unit="K",
            )
        )

        # Pump
        self.system.add_sensor(
            Sensor(
                name="pump_hydraulic_power",
                unit="MW",
            )
        )

    def _create_actuators(self):
        self.system.add_actuator(
            Actuator(
                name="reactor_power_control",
            )
        )

        self.system.add_actuator(
            Actuator(
                name="scram",
            )
        )

    def update(self, state: "PlantState") -> None:
        timestamp = state.time_s

        # Reactor
        self.system.get_sensor(
            "reactor_power"
        ).update(
            state.power_mw,
            timestamp,
        )

        self.system.get_sensor(
            "reactor_temperature"
        ).update(
            state.temperature_k,
            timestamp,
        )

        self.system.get_sensor(
            "neutron_population"
        ).update(
            state.neutron_population,
            timestamp,
        )

        self.system.get_sensor(
            "reactivity"
        ).update(
            state.total_reactivity,
            timestamp,
        )

        # Thermal
        self.system.get_sensor(
            "transferred_power"
        ).update(
            state.transferred_power_mw,
            timestamp,
        )

        self.system.get_sensor(
            "thermal_losses"
        ).update(
            state.lost_thermal_power_mw,
            timestamp,
        )

        self.system.get_sensor(
            "useful_thermal_power"
        ).update(
            state.useful_thermal_power_mw,
            timestamp,
        )

        self.system.get_sensor(
            "coolant_outlet_temperature"
        ).update(
            state.coolant_outlet_temperature_k,
            timestamp,
        )

        # Steam / turbine
        self.system.get_sensor(
            "steam_power"
        ).update(
            state.steam_power_mw,
            timestamp,
        )

        self.system.get_sensor(
            "mechanical_power"
        ).update(
            state.mechanical_power_mw,
            timestamp,
        )

        self.system.get_sensor(
            "turbine_speed"
        ).update(
            state.turbine_speed_rpm,
            timestamp,
        )

        # Electrical
        self.system.get_sensor(
            "electrical_power"
        ).update(
            state.electrical_power_mw,
            timestamp,
        )

        self.system.get_sensor(
            "net_electrical_power"
        ).update(
            state.net_electrical_power_mw,
            timestamp,
        )

        # Condenser
        self.system.get_sensor(
            "rejected_heat"
        ).update(
            state.rejected_heat_mw,
            timestamp,
        )

        self.system.get_sensor(
            "condensed_heat"
        ).update(
            state.condensed_heat_mw,
            timestamp,
        )

        self.system.get_sensor(
            "condenser_outlet_temperature"
        ).update(
            state.condenser_outlet_temperature_k,
            timestamp,
        )

        # Pump
        self.system.get_sensor(
            "pump_hydraulic_power"
        ).update(
            state.pump_hydraulic_power_mw,
            timestamp,
        )

    def sensor_readings(self):
        return {
            name: sensor.read()
            for name, sensor in self.system._sensors.items()
        }

    def actuator_states(self):
        return {
            name: actuator.state()
            for name, actuator in self.system._actuators.items()
        }