from dataclasses import dataclass

from nuclear_sim.plant.reactor import Reactor
from nuclear_sim.plant.reactor_dynamics import ReactorDynamics
from nuclear_sim.thermal.energy_balance import EnergyBalanceState
from nuclear_sim.thermal.thermal_model import ThermalModel
from nuclear_sim.thermal.power_cycle import PowerCycle
from nuclear_sim.plant.plant_instrumentation import PlantInstrumentation
from nuclear_sim.plant.plant_controller import PlantController
from nuclear_sim.telemetry.collector import TelemetryCollector

@dataclass(frozen=True)
class PlantState:
    time_s: float
    power_mw: float
    temperature_k: float
    reactor_status: str

    electrical_power_mw: float
    auxiliary_power_mw: float
    net_electrical_power_mw: float

    external_reactivity: float = 0.0
    temperature_reactivity: float = 0.0
    total_reactivity: float = 0.0

    energy_balance: EnergyBalanceState | None = None

    neutron_population: float = 0.0

    transferred_power_mw: float = 0.0
    lost_thermal_power_mw: float = 0.0
    useful_thermal_power_mw: float = 0.0
    coolant_outlet_temperature_k: float = 0.0
    steam_power_mw: float = 0.0
    mechanical_power_mw: float = 0.0
    turbine_speed_rpm: float = 0.0

    rejected_heat_mw: float = 0.0
    condensed_heat_mw: float = 0.0
    condenser_outlet_temperature_k: float = 0.0
    
    pump_hydraulic_power_mw: float = 0.0


class PlantSimulation:
    def __init__(
        self,
        reactor: Reactor,
        thermal_model: ThermalModel,
        power_cycle: PowerCycle | None = None,
        reactor_dynamics: ReactorDynamics | None = None,
        instrumentation: PlantInstrumentation | None = None,
        controller: PlantController | None = None,
        telemetry_collector: TelemetryCollector | None = None,
    ):
        self.reactor = reactor
        self.thermal_model = thermal_model
        self.power_cycle = power_cycle
        self.reactor_dynamics = reactor_dynamics
        self.instrumentation = instrumentation
        self.controller = controller
        self.telemetry_collector = telemetry_collector
        self._state = PlantState(
            time_s=0.0,
            power_mw=reactor.state().power_mw,
            temperature_k=thermal_model.temperature_k,
            reactor_status=reactor.state().status,
            electrical_power_mw=0.0,
            auxiliary_power_mw=0.0,
            net_electrical_power_mw=0.0,
            energy_balance = None,
        )

    def state(self) -> PlantState:
        return self._state

    def step(
        self,
        dt_s: float,
        heat_removed_mw: float,
        external_reactivity: float | None = None,
    ) -> PlantState:

        if self.reactor_dynamics is not None:
            if self.controller is not None:
                self.controller.update_control()

            dynamics_state = self.reactor_dynamics.step(
                dt_s=dt_s,
                heat_removed_mw=heat_removed_mw,
                external_reactivity=external_reactivity,
            )

            power_mw = dynamics_state.power_mw
            temperature_k = dynamics_state.temperature_k
            neutron_population = dynamics_state.neutron_population
            external_rho = dynamics_state.external_reactivity
            temperature_rho = dynamics_state.temperature_reactivity
            total_rho = dynamics_state.total_reactivity

            time_s = dynamics_state.time_s

        else:
            self.thermal_model.step(
                thermal_power_mw=self.reactor.state().power_mw,
                heat_removed_mw=heat_removed_mw,
                dt_s=dt_s,
            )

            power_mw = self.reactor.state().power_mw
            temperature_k = self.thermal_model.temperature_k

            external_rho = (
                0.0 if external_reactivity is None else external_reactivity
            )
            temperature_rho = 0.0
            total_rho = external_rho

            time_s = self._state.time_s + dt_s

        electrical_power_mw = 0.0
        auxiliary_power_mw = 0.0
        net_electrical_power_mw = 0.0
        energy_balance = None

        neutron_population = 0.0

        transferred_power_mw = 0.0
        lost_thermal_power_mw = 0.0
        useful_thermal_power_mw = 0.0
        coolant_outlet_temperature_k = 0.0
        steam_power_mw = 0.0
        mechanical_power_mw = 0.0
        turbine_speed_rpm = 0.0

        rejected_heat_mw = 0.0
        condensed_heat_mw = 0.0
        condenser_outlet_temperature_k = 0.0

        pump_hydraulic_power_mw = 0.0

        if self.power_cycle is not None:
            cycle_state = self.power_cycle.run(
                reactor_power_mw=power_mw,
                primary_temperature_k=temperature_k,
            )

            electrical_power_mw = cycle_state.electrical_power_mw
            auxiliary_power_mw = cycle_state.pump_electrical_power_mw
            net_electrical_power_mw = cycle_state.net_electrical_power_mw
            energy_balance = cycle_state.energy_balance
            transferred_power_mw = cycle_state.transferred_power_mw
            lost_thermal_power_mw = cycle_state.lost_thermal_power_mw
            useful_thermal_power_mw = cycle_state.useful_thermal_power_mw

            coolant_outlet_temperature_k = (
                cycle_state.coolant_outlet_temperature_k
            )

            steam_power_mw = cycle_state.steam_power_mw
            mechanical_power_mw = cycle_state.mechanical_power_mw
            turbine_speed_rpm = cycle_state.turbine_speed_rpm

            rejected_heat_mw = cycle_state.rejected_heat_mw
            condensed_heat_mw = cycle_state.condensed_heat_mw

            condenser_outlet_temperature_k = (
                cycle_state.condenser_outlet_temperature_k
            )

            pump_hydraulic_power_mw = (
                cycle_state.pump_hydraulic_power_mw
            )

        reactor_status = self._status_from_power(power_mw)

        self._state = PlantState(
            time_s=time_s,
            power_mw=power_mw,
            temperature_k=temperature_k,
            reactor_status=reactor_status,
            electrical_power_mw=electrical_power_mw,
            auxiliary_power_mw=auxiliary_power_mw,
            net_electrical_power_mw=net_electrical_power_mw,
            external_reactivity=external_rho,
            temperature_reactivity=temperature_rho,
            total_reactivity=total_rho,
            energy_balance=energy_balance,
            neutron_population=neutron_population,
            transferred_power_mw=transferred_power_mw,
            lost_thermal_power_mw=lost_thermal_power_mw,
            useful_thermal_power_mw=useful_thermal_power_mw,
            coolant_outlet_temperature_k=(
                coolant_outlet_temperature_k
            ),
            steam_power_mw=steam_power_mw,
            mechanical_power_mw=mechanical_power_mw,
            turbine_speed_rpm=turbine_speed_rpm,
            rejected_heat_mw=rejected_heat_mw,
            condensed_heat_mw=condensed_heat_mw,
            condenser_outlet_temperature_k=(
                condenser_outlet_temperature_k
            ),

            pump_hydraulic_power_mw=pump_hydraulic_power_mw,
        )

        if self.instrumentation is not None:
            self.instrumentation.update(self._state)

        if self.telemetry_collector is not None:
            self.telemetry_collector.collect(self._state)

        return self._state
    def set_reactor_power(self, power_fraction: float):
        """Establece la potencia del reactor mediante el controlador."""

        if self.controller is None:
            raise RuntimeError("PlantSimulation no tiene un controlador configurado.")

        return self.controller.set_reactor_power(
            power_fraction=power_fraction,
            timestamp_s=self._state.time_s,
        )


    def scram(self):
        """Activa el SCRAM mediante el controlador."""

        if self.controller is None:
            raise RuntimeError("PlantSimulation no tiene un controlador configurado.")

        return self.controller.scram(
            timestamp_s=self._state.time_s,
        )

    def _status_from_power(self, power_mw: float) -> str:
        if power_mw <= 0.0:
            return "shutdown"

        fraction = power_mw / self.reactor.rated_power_mw

        if fraction < 0.05:
            return "startup"

        if fraction < 0.95:
            return "operating"

        return "full_power"