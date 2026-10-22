from dataclasses import dataclass

from nuclear_sim.thermal.coolant import Coolant
from nuclear_sim.thermal.generator import Generator
from nuclear_sim.thermal.heat_transfer import HeatTransferModel
from nuclear_sim.thermal.steam_generator import SteamGenerator
from nuclear_sim.thermal.turbine import Turbine
from nuclear_sim.thermal.heat_exchanger import HeatExchanger
from nuclear_sim.thermal.condenser import Condenser
from nuclear_sim.thermal.pump import Pump
from nuclear_sim.thermal.thermal_losses import ThermalLossModel
from nuclear_sim.thermal.energy_balance import EnergyBalanceState, EnergyBalance


@dataclass(frozen=True)
class PowerCycleState:
    """Estado completo del ciclo de conversión energética."""

    reactor_power_mw: float
    transferred_power_mw: float

    heat_exchanger_power_mw: float = 0.0
    heat_exchanger_lmtd_k: float = 0.0

    lost_thermal_power_mw: float = 0.0
    useful_thermal_power_mw: float = 0.0

    coolant_outlet_temperature_k: float = 0.0

    steam_power_mw: float = 0.0
    mechanical_power_mw: float = 0.0
    electrical_power_mw: float = 0.0
    turbine_speed_rpm: float = 0.0

    rejected_heat_mw: float = 0.0
    condensed_heat_mw: float = 0.0
    condenser_outlet_temperature_k: float = 0.0

    pump_hydraulic_power_mw: float = 0.0
    pump_electrical_power_mw: float = 0.0
    net_electrical_power_mw: float = 0.0

    energy_balance: EnergyBalanceState | None = None
    


class PowerCycle:
    """Integra el circuito térmico y la conversión eléctrica."""

    def __init__(
        self,
        coolant: Coolant,
        heat_transfer: HeatTransferModel,
        steam_generator: SteamGenerator,
        turbine: Turbine,
        generator: Generator,
        heat_exchanger: HeatExchanger | None = None,
        condenser: Condenser | None = None,
        pump: Pump | None = None,
        thermal_losses: ThermalLossModel | None = None,
        secondary_mass_flow_kg_s: float = 1000.0,
        secondary_specific_heat_kj_kg_k: float = 4.18,
        pump_inlet_pressure_mpa: float = 0.1,
        pump_outlet_pressure_mpa: float = 15.5,
    ) -> None:
        self.coolant = coolant
        self.heat_transfer = heat_transfer
        self.steam_generator = steam_generator
        self.turbine = turbine
        self.generator = generator

        self.heat_exchanger = heat_exchanger
        self.condenser = condenser
        self.pump = pump

        self.thermal_losses = (
            thermal_losses
            if thermal_losses is not None
            else ThermalLossModel()
        )

        self.energy_balance = EnergyBalance()

        self.secondary_mass_flow_kg_s = (
            secondary_mass_flow_kg_s
        )

        self.secondary_specific_heat_kj_kg_k = (
            secondary_specific_heat_kj_kg_k
        )

        self.pump_inlet_pressure_mpa = (
            pump_inlet_pressure_mpa
        )

        self.pump_outlet_pressure_mpa = (
            pump_outlet_pressure_mpa
        )

    def run(
        self,
        reactor_power_mw: float,
        primary_temperature_k: float,
    ) -> PowerCycleState:

        transfer_state = self.heat_transfer.transfer(
            reactor_power_mw
        )

        transferred_power_mw = (
            transfer_state.transferred_power_mw
        )

        heat_exchanger_power_mw = transferred_power_mw
        heat_exchanger_lmtd_k = 0.0

        if (
            self.heat_exchanger is not None
            and transferred_power_mw > 0.0
        ):
            hot_inlet_temperature_k = (
                primary_temperature_k
            )

            hot_outlet_temperature_k = (
                self.coolant.calculate_outlet_temperature(
                    transferred_power_mw
                )
            )

            cold_inlet_temperature_k = (
                self.steam_generator.reference_temperature_k
            )

            cold_outlet_temperature_k = (
                cold_inlet_temperature_k
                + (
                    transferred_power_mw
                    / (
                        self.secondary_mass_flow_kg_s
                        * self.secondary_specific_heat_kj_kg_k
                        / 1000.0
                    )
                )
            )

            exchanger_state = self.heat_exchanger.solve(
                hot_inlet_temperature_k=(
                    hot_inlet_temperature_k
                ),
                cold_inlet_temperature_k=(
                    cold_inlet_temperature_k
                ),
                hot_mass_flow_kg_s=(
                    self.coolant.mass_flow_kg_s
                ),
                cold_mass_flow_kg_s=(
                    self.secondary_mass_flow_kg_s
                ),
                hot_specific_heat_kj_kg_k=(
                    self.coolant.specific_heat_kj_kg_k
                ),
                cold_specific_heat_kj_kg_k=(
                    self.secondary_specific_heat_kj_kg_k
                ),
            )

            heat_exchanger_power_mw = (
                exchanger_state.heat_transfer_mw
            )

            heat_exchanger_lmtd_k = (
                exchanger_state.log_mean_temperature_difference_k
            )

        loss_state = self.thermal_losses.calculate(
            transferred_power_mw
        )

        useful_thermal_power_mw = (
            loss_state.useful_power_mw
        )

        coolant_temperature = (
            self.coolant.calculate_outlet_temperature(
                useful_thermal_power_mw
            )
        )

        steam_state = self.steam_generator.generate(
            thermal_power_mw=useful_thermal_power_mw,
            primary_temperature_k=primary_temperature_k,
        )

        turbine_state = self.turbine.expand(
            steam_state.steam_power_mw
        )

        generator_state = self.generator.generate(
            turbine_state.mechanical_power_mw
        )

        rejected_heat_mw = 0.0
        condensed_heat_mw = 0.0
        condenser_outlet_temperature_k = 0.0

        energy_balance_rejected_heat_mw = (
            steam_state.steam_power_mw
            - turbine_state.mechanical_power_mw
        )

        if self.condenser is not None:
            condenser_state = self.condenser.condense(
                steam_power_mw=steam_state.steam_power_mw,
                mechanical_power_mw=(
                    turbine_state.mechanical_power_mw
                ),
                inlet_temperature_k=(
                    steam_state.steam_temperature_k
                ),
            )

            rejected_heat_mw = (
                condenser_state.rejected_heat_mw
            )

            condensed_heat_mw = (
                condenser_state.condensed_heat_mw
            )

            condenser_outlet_temperature_k = (
                condenser_state.outlet_temperature_k
            )

        pump_hydraulic_power_mw = 0.0
        pump_electrical_power_mw = 0.0
        net_electrical_power_mw = generator_state.electrical_power_mw

        if (
            self.pump is not None
            and steam_state.steam_power_mw > 0.0
        ):
            pump_inlet_temperature_k = (
                condenser_outlet_temperature_k
                if condenser_outlet_temperature_k > 0.0
                else self.steam_generator.reference_temperature_k
            )

            pump_state = self.pump.pump(
                mass_flow_kg_s=(
                    self.secondary_mass_flow_kg_s
                ),
                inlet_pressure_mpa=(
                    self.pump_inlet_pressure_mpa
                ),
                outlet_pressure_mpa=(
                    self.pump_outlet_pressure_mpa
                ),
                inlet_temperature_k=(
                    pump_inlet_temperature_k
                ),
            )

            pump_hydraulic_power_mw = (
                pump_state.hydraulic_power_mw
            )

            pump_electrical_power_mw = (
                pump_state.electrical_power_mw
            )

            net_electrical_power_mw = (
                    generator_state.electrical_power_mw
                    - pump_electrical_power_mw
                )

        energy_balance_state = None

        if (
            reactor_power_mw > 0.0
        ):
            energy_balance_state = self.energy_balance.calculate(
                input_power_mw=transferred_power_mw,
                thermal_losses_mw=loss_state.lost_power_mw,
                useful_thermal_power_mw=useful_thermal_power_mw,
                steam_power_mw=steam_state.steam_power_mw,
                mechanical_power_mw=turbine_state.mechanical_power_mw,
                electrical_power_mw=generator_state.electrical_power_mw,
                rejected_heat_mw=energy_balance_rejected_heat_mw,
                auxiliary_power_mw=pump_electrical_power_mw,
            )

        return PowerCycleState(
            reactor_power_mw=reactor_power_mw,
            transferred_power_mw=transferred_power_mw,
            heat_exchanger_power_mw=(
                heat_exchanger_power_mw
            ),
            heat_exchanger_lmtd_k=(
                heat_exchanger_lmtd_k
            ),
            lost_thermal_power_mw=(
                loss_state.lost_power_mw
            ),
            useful_thermal_power_mw=(
                useful_thermal_power_mw
            ),
            coolant_outlet_temperature_k=(
                coolant_temperature
            ),
            steam_power_mw=(
                steam_state.steam_power_mw
            ),
            mechanical_power_mw=(
                turbine_state.mechanical_power_mw
            ),
            electrical_power_mw=(
                generator_state.electrical_power_mw
            ),
            turbine_speed_rpm=(
                turbine_state.rotational_speed_rpm
            ),
            rejected_heat_mw=rejected_heat_mw,
            condensed_heat_mw=condensed_heat_mw,
            condenser_outlet_temperature_k=(
                condenser_outlet_temperature_k
            ),
            pump_hydraulic_power_mw=(
                pump_hydraulic_power_mw
            ),
            pump_electrical_power_mw=(
                pump_electrical_power_mw
            ),
            net_electrical_power_mw=(
                net_electrical_power_mw
            ),
            energy_balance=energy_balance_state,
        )