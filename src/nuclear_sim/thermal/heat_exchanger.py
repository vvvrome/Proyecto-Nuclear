from dataclasses import dataclass
import math


@dataclass(frozen=True)
class HeatExchangerState:
    """Estado instantáneo del intercambiador de calor."""

    heat_transfer_mw: float
    log_mean_temperature_difference_k: float
    overall_heat_transfer_coefficient_w_m2_k: float
    heat_transfer_area_m2: float

    @property
    def heat_rate_w(self) -> float:
        return self.heat_transfer_mw * 1.0e6

    @property
    def lmtd_k(self) -> float:
        return self.log_mean_temperature_difference_k


@dataclass(frozen=True)
class HeatExchangerFlowState:
    """Estado del intercambiador calculado mediante balances de energía."""

    heat_transfer_mw: float
    hot_inlet_temperature_k: float
    hot_outlet_temperature_k: float
    cold_inlet_temperature_k: float
    cold_outlet_temperature_k: float
    log_mean_temperature_difference_k: float


class HeatExchanger:
    """Modelo de intercambiador basado en UA·ΔTlm."""

    def __init__(
        self,
        overall_heat_transfer_coefficient_w_m2_k: float,
        heat_transfer_area_m2: float,
    ) -> None:
        if (
            not math.isfinite(
                overall_heat_transfer_coefficient_w_m2_k
            )
            or overall_heat_transfer_coefficient_w_m2_k <= 0
        ):
            raise ValueError(
                "El coeficiente global de transferencia debe "
                "ser positivo y finito."
            )

        if (
            not math.isfinite(heat_transfer_area_m2)
            or heat_transfer_area_m2 <= 0
        ):
            raise ValueError(
                "El área de transferencia debe ser positiva y finita."
            )

        self.overall_heat_transfer_coefficient_w_m2_k = float(
            overall_heat_transfer_coefficient_w_m2_k
        )

        self.heat_transfer_area_m2 = float(
            heat_transfer_area_m2
        )

    @staticmethod
    def _logarithmic_mean(
        delta_t_1: float,
        delta_t_2: float,
    ) -> float:
        if delta_t_1 <= 0 or delta_t_2 <= 0:
            raise ValueError(
                "Las diferencias de temperatura deben ser positivas."
            )

        if math.isclose(
            delta_t_1,
            delta_t_2,
            rel_tol=1.0e-12,
            abs_tol=1.0e-12,
        ):
            return delta_t_1

        return (
            (delta_t_1 - delta_t_2)
            / math.log(delta_t_1 / delta_t_2)
        )

    @staticmethod
    def log_mean_temperature_difference(
        hot_inlet_temperature_k: float,
        hot_outlet_temperature_k: float,
        cold_inlet_temperature_k: float,
        cold_outlet_temperature_k: float,
    ) -> float:
        """Calcula la diferencia logarítmica media de temperatura."""

        temperatures = (
            hot_inlet_temperature_k,
            hot_outlet_temperature_k,
            cold_inlet_temperature_k,
            cold_outlet_temperature_k,
        )

        if any(
            not math.isfinite(temperature)
            or temperature <= 0
            for temperature in temperatures
        ):
            raise ValueError(
                "Todas las temperaturas deben ser positivas y finitas."
            )

        delta_t_1 = (
            hot_inlet_temperature_k
            - cold_outlet_temperature_k
        )

        delta_t_2 = (
            hot_outlet_temperature_k
            - cold_inlet_temperature_k
        )

        return HeatExchanger._logarithmic_mean(
            delta_t_1,
            delta_t_2,
        )

    def lmtd(
        self,
        delta_t_1: float,
        delta_t_2: float,
    ) -> float:
        """Calcula la diferencia logarítmica media directamente."""

        if (
            not math.isfinite(delta_t_1)
            or not math.isfinite(delta_t_2)
        ):
            raise ValueError(
                "Las diferencias de temperatura deben ser finitas."
            )

        return self._logarithmic_mean(
            delta_t_1,
            delta_t_2,
        )

    def transfer(
        self,
        hot_inlet_temperature_k: float,
        hot_outlet_temperature_k: float,
        cold_inlet_temperature_k: float,
        cold_outlet_temperature_k: float,
    ) -> HeatExchangerState:
        """Calcula la potencia transferida mediante UA·ΔTlm."""

        delta_t_lm = self.log_mean_temperature_difference(
            hot_inlet_temperature_k=hot_inlet_temperature_k,
            hot_outlet_temperature_k=hot_outlet_temperature_k,
            cold_inlet_temperature_k=cold_inlet_temperature_k,
            cold_outlet_temperature_k=cold_outlet_temperature_k,
        )

        heat_transfer_w = (
            self.overall_heat_transfer_coefficient_w_m2_k
            * self.heat_transfer_area_m2
            * delta_t_lm
        )

        heat_transfer_mw = heat_transfer_w / 1.0e6

        return HeatExchangerState(
            heat_transfer_mw=heat_transfer_mw,
            log_mean_temperature_difference_k=delta_t_lm,
            overall_heat_transfer_coefficient_w_m2_k=(
                self.overall_heat_transfer_coefficient_w_m2_k
            ),
            heat_transfer_area_m2=self.heat_transfer_area_m2,
        )

    def calculate(
        self,
        hot_inlet_temperature_k: float,
        hot_outlet_temperature_k: float,
        cold_inlet_temperature_k: float,
        cold_outlet_temperature_k: float,
    ) -> HeatExchangerState:
        """Alias compatible con la API anterior."""

        return self.transfer(
            hot_inlet_temperature_k=hot_inlet_temperature_k,
            hot_outlet_temperature_k=hot_outlet_temperature_k,
            cold_inlet_temperature_k=cold_inlet_temperature_k,
            cold_outlet_temperature_k=cold_outlet_temperature_k,
        )

    def solve(
        self,
        hot_inlet_temperature_k: float,
        cold_inlet_temperature_k: float,
        hot_mass_flow_kg_s: float,
        cold_mass_flow_kg_s: float,
        hot_specific_heat_kj_kg_k: float,
        cold_specific_heat_kj_kg_k: float,
        tolerance_mw: float = 1.0e-9,
        max_iterations: int = 100,
    ) -> HeatExchangerFlowState:
        """
        Resuelve el intercambiador mediante balances de energía.

        Q = UA·ΔTlm

        Q = Ch·(Th,in - Th,out)

        Q = Cc·(Tc,out - Tc,in)
        """

        values = (
            hot_inlet_temperature_k,
            cold_inlet_temperature_k,
            hot_mass_flow_kg_s,
            cold_mass_flow_kg_s,
            hot_specific_heat_kj_kg_k,
            cold_specific_heat_kj_kg_k,
            tolerance_mw,
        )

        if any(
            not math.isfinite(value)
            for value in values
        ):
            raise ValueError(
                "Todos los parámetros deben ser finitos."
            )

        if hot_inlet_temperature_k <= cold_inlet_temperature_k:
            raise ValueError(
                "La temperatura de entrada caliente debe ser "
                "mayor que la fría."
            )

        if hot_mass_flow_kg_s <= 0 or cold_mass_flow_kg_s <= 0:
            raise ValueError(
                "Los caudales másicos deben ser positivos."
            )

        if (
            hot_specific_heat_kj_kg_k <= 0
            or cold_specific_heat_kj_kg_k <= 0
        ):
            raise ValueError(
                "Los calores específicos deben ser positivos."
            )

        if tolerance_mw <= 0:
            raise ValueError(
                "La tolerancia debe ser positiva."
            )

        if max_iterations <= 0:
            raise ValueError(
                "El número máximo de iteraciones debe ser positivo."
            )

        ua_mw_per_k = (
            self.overall_heat_transfer_coefficient_w_m2_k
            * self.heat_transfer_area_m2
            / 1.0e6
        )

        hot_capacity_mw_per_k = (
            hot_mass_flow_kg_s
            * hot_specific_heat_kj_kg_k
            / 1000.0
        )

        cold_capacity_mw_per_k = (
            cold_mass_flow_kg_s
            * cold_specific_heat_kj_kg_k
            / 1000.0
        )

        maximum_heat_transfer_mw = (
            min(
                hot_capacity_mw_per_k,
                cold_capacity_mw_per_k,
            )
            * (
                hot_inlet_temperature_k
                - cold_inlet_temperature_k
            )
            * (1.0 - 1.0e-12)
        )

        def residual(heat_transfer_mw: float) -> float:
            hot_outlet = (
                hot_inlet_temperature_k
                - heat_transfer_mw
                / hot_capacity_mw_per_k
            )

            cold_outlet = (
                cold_inlet_temperature_k
                + heat_transfer_mw
                / cold_capacity_mw_per_k
            )

            delta_t_1 = (
                hot_inlet_temperature_k
                - cold_outlet
            )

            delta_t_2 = (
                hot_outlet
                - cold_inlet_temperature_k
            )

            if delta_t_1 <= 0 or delta_t_2 <= 0:
                return -heat_transfer_mw

            delta_t_lm = self._logarithmic_mean(
                delta_t_1,
                delta_t_2,
            )

            calculated_heat = (
                ua_mw_per_k * delta_t_lm
            )

            return calculated_heat - heat_transfer_mw

        lower = 0.0
        upper = maximum_heat_transfer_mw

        for _ in range(max_iterations):
            middle = (lower + upper) / 2.0
            error = residual(middle)

            if abs(error) <= tolerance_mw:
                heat_transfer_mw = middle
                break

            if error > 0:
                lower = middle
            else:
                upper = middle
        else:
            heat_transfer_mw = (
                lower + upper
            ) / 2.0

        hot_outlet_temperature_k = (
            hot_inlet_temperature_k
            - heat_transfer_mw
            / hot_capacity_mw_per_k
        )

        cold_outlet_temperature_k = (
            cold_inlet_temperature_k
            + heat_transfer_mw
            / cold_capacity_mw_per_k
        )

        delta_t_lm = self.log_mean_temperature_difference(
            hot_inlet_temperature_k=hot_inlet_temperature_k,
            hot_outlet_temperature_k=hot_outlet_temperature_k,
            cold_inlet_temperature_k=cold_inlet_temperature_k,
            cold_outlet_temperature_k=cold_outlet_temperature_k,
        )

        return HeatExchangerFlowState(
            heat_transfer_mw=heat_transfer_mw,
            hot_inlet_temperature_k=hot_inlet_temperature_k,
            hot_outlet_temperature_k=hot_outlet_temperature_k,
            cold_inlet_temperature_k=cold_inlet_temperature_k,
            cold_outlet_temperature_k=cold_outlet_temperature_k,
            log_mean_temperature_difference_k=delta_t_lm,
        )