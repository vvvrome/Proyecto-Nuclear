from dataclasses import dataclass
import math


@dataclass(frozen=True)
class PointKineticsState:
    """Estado de la cinética puntual."""

    neutron_population: float
    precursor_population: float
    time_s: float = 0.0
    reactivity: float = 0.0

    @property
    def normalized_power(self) -> float:
        """Potencia normalizada respecto a la potencia inicial."""

        return self.neutron_population


class PointKinetics:
    """Modelo de cinética puntual de un grupo de neutrones retardados.

    Ecuaciones:

        dn/dt = ((rho - beta) / Lambda) * n + lambda * C

        dC/dt = (beta / Lambda) * n - lambda * C

    donde:

        n      = población neutrónica relativa
        C      = concentración de precursores
        rho    = reactividad
        beta   = fracción de neutrones retardados
        Lambda = tiempo de generación de neutrones
        lambda = constante de decaimiento del precursor

    La integración temporal utiliza Runge-Kutta de cuarto orden (RK4).
    """

    def __init__(
        self,
        beta: float = 0.0065,
        generation_time_s: float = 1.0e-4,
        precursor_decay_constant_per_s: float = 0.08,
    ) -> None:
        if not math.isfinite(beta) or not 0.0 < beta < 1.0:
            raise ValueError(
                "beta debe estar entre 0 y 1."
            )

        if (
            not math.isfinite(generation_time_s)
            or generation_time_s <= 0
        ):
            raise ValueError(
                "El tiempo de generación debe ser positivo y finito."
            )

        if (
            not math.isfinite(precursor_decay_constant_per_s)
            or precursor_decay_constant_per_s <= 0
        ):
            raise ValueError(
                "La constante de decaimiento debe ser positiva y finita."
            )

        self.beta = float(beta)
        self.generation_time_s = float(generation_time_s)
        self.precursor_decay_constant_per_s = float(
            precursor_decay_constant_per_s
        )

        # Estado interno.
        self._time_s = 0.0
        self._reactivity = 0.0

        # Población neutrónica normalizada.
        self._neutron_population = 1.0

        # Estado inicial de equilibrio para rho = 0.
        self._precursor_population = (
            self.equilibrium_precursor_population(
                self._neutron_population
            )
        )

    def equilibrium_precursor_population(
        self,
        neutron_population: float,
    ) -> float:
        """Calcula la población de precursores en equilibrio.

        Para rho = 0:

            dC/dt = 0

        y por tanto:

            C_eq = beta / (Lambda * lambda) * n
        """

        if (
            not math.isfinite(neutron_population)
            or neutron_population < 0
        ):
            raise ValueError(
                "La población neutrónica debe ser finita y no negativa."
            )

        return (
            self.beta
            / (
                self.generation_time_s
                * self.precursor_decay_constant_per_s
            )
            * neutron_population
        )

    def equilibrium_state(
        self,
        neutron_population: float = 1.0,
    ) -> PointKineticsState:
        """Devuelve el estado de equilibrio para rho = 0."""

        if (
            not math.isfinite(neutron_population)
            or neutron_population < 0
        ):
            raise ValueError(
                "La población neutrónica debe ser finita y no negativa."
            )

        return PointKineticsState(
            neutron_population=neutron_population,
            precursor_population=(
                self.equilibrium_precursor_population(
                    neutron_population
                )
            ),
            time_s=0.0,
            reactivity=0.0,
        )

    def derivatives(
        self,
        neutron_population: float,
        precursor_population: float,
        reactivity: float,
    ) -> tuple[float, float]:
        """Calcula dn/dt y dC/dt."""

        if (
            not math.isfinite(neutron_population)
            or neutron_population < 0
        ):
            raise ValueError(
                "La población neutrónica debe ser finita y no negativa."
            )

        if (
            not math.isfinite(precursor_population)
            or precursor_population < 0
        ):
            raise ValueError(
                "La población de precursores debe ser finita y no negativa."
            )

        if not math.isfinite(reactivity):
            raise ValueError(
                "La reactividad debe ser finita."
            )

        dn_dt = (
            (reactivity - self.beta)
            / self.generation_time_s
            * neutron_population
            + self.precursor_decay_constant_per_s
            * precursor_population
        )

        dC_dt = (
            self.beta
            / self.generation_time_s
            * neutron_population
            - self.precursor_decay_constant_per_s
            * precursor_population
        )

        return dn_dt, dC_dt

    def _rk4_step(
        self,
        neutron_population: float,
        precursor_population: float,
        reactivity: float,
        dt_s: float,
    ) -> tuple[float, float]:
        """Realiza un paso interno RK4.

        Los estados intermedios se limitan a cero para evitar que
        errores numéricos del integrador produzcan poblaciones
        físicamente negativas.
        """

        k1_n, k1_c = self.derivatives(
            neutron_population,
            precursor_population,
            reactivity,
        )

        n2 = max(
            neutron_population + 0.5 * dt_s * k1_n,
            0.0,
        )
        c2 = max(
            precursor_population + 0.5 * dt_s * k1_c,
            0.0,
        )

        k2_n, k2_c = self.derivatives(
            n2,
            c2,
            reactivity,
        )

        n3 = max(
            neutron_population + 0.5 * dt_s * k2_n,
            0.0,
        )
        c3 = max(
            precursor_population + 0.5 * dt_s * k2_c,
            0.0,
        )

        k3_n, k3_c = self.derivatives(
            n3,
            c3,
            reactivity,
        )

        n4 = max(
            neutron_population + dt_s * k3_n,
            0.0,
        )
        c4 = max(
            precursor_population + dt_s * k3_c,
            0.0,
        )

        k4_n, k4_c = self.derivatives(
            n4,
            c4,
            reactivity,
        )

        new_neutron_population = (
            neutron_population
            + (dt_s / 6.0)
            * (
                k1_n
                + 2.0 * k2_n
                + 2.0 * k3_n
                + k4_n
            )
        )

        new_precursor_population = (
            precursor_population
            + (dt_s / 6.0)
            * (
                k1_c
                + 2.0 * k2_c
                + 2.0 * k3_c
                + k4_c
            )
        )

        return (
            max(new_neutron_population, 0.0),
            max(new_precursor_population, 0.0),
        )

    def step(
        self,
        neutron_population: float,
        precursor_population: float,
        reactivity: float,
        dt_s: float,
    ) -> PointKineticsState:
        """Avanza la cinética mediante RK4 con subpasos adaptados."""

        if (
            not math.isfinite(neutron_population)
            or neutron_population < 0
        ):
            raise ValueError(
                "La población neutrónica debe ser finita y no negativa."
            )

        if (
            not math.isfinite(precursor_population)
            or precursor_population < 0
        ):
            raise ValueError(
                "La población de precursores debe ser finita y no negativa."
            )

        if not math.isfinite(reactivity):
            raise ValueError(
                "La reactividad debe ser finita."
            )

        if not math.isfinite(dt_s) or dt_s < 0:
            raise ValueError(
                "El intervalo de tiempo debe ser finito y no negativo."
            )

        if dt_s == 0.0:
            return PointKineticsState(
                neutron_population=neutron_population,
                precursor_population=precursor_population,
                time_s=0.0,
                reactivity=reactivity,
            )

        # La cinética puntual puede ser un sistema rígido porque
        # el tiempo de generación de neutrones es muy pequeño.
        #
        # Para evitar que un paso grande destruya la estabilidad
        # numérica, dividimos automáticamente el intervalo.
        maximum_step = min(
            dt_s,
            self.generation_time_s * 0.1,
        )

        number_of_steps = max(
            1,
            math.ceil(dt_s / maximum_step),
        )

        substep = dt_s / number_of_steps

        current_neutron_population = neutron_population
        current_precursor_population = precursor_population

        for _ in range(number_of_steps):
            (
                current_neutron_population,
                current_precursor_population,
            ) = self._rk4_step(
                neutron_population=current_neutron_population,
                precursor_population=current_precursor_population,
                reactivity=reactivity,
                dt_s=substep,
            )

        return PointKineticsState(
            neutron_population=current_neutron_population,
            precursor_population=current_precursor_population,
            time_s=dt_s,
            reactivity=reactivity,
        )

    def set_reactivity(self, reactivity: float) -> None:
        """Establece la reactividad utilizada por la simulación."""

        if not math.isfinite(reactivity):
            raise ValueError(
                "La reactividad debe ser finita."
            )

        self._reactivity = float(reactivity)

    def state(self) -> PointKineticsState:
        """Devuelve el estado cinético actual."""

        return PointKineticsState(
            neutron_population=self._neutron_population,
            precursor_population=self._precursor_population,
            time_s=self._time_s,
            reactivity=self._reactivity,
        )

    def advance(self, dt_s: float) -> PointKineticsState:
        """Avanza el estado interno mediante RK4."""

        if not math.isfinite(dt_s) or dt_s < 0:
            raise ValueError(
                "El intervalo de tiempo debe ser finito y no negativo."
            )

        if dt_s == 0.0:
            return self.state()

        state = self.step(
            neutron_population=self._neutron_population,
            precursor_population=self._precursor_population,
            reactivity=self._reactivity,
            dt_s=dt_s,
        )

        self._neutron_population = state.neutron_population
        self._precursor_population = state.precursor_population
        self._time_s += dt_s

        return self.state()

    @property
    def time_s(self) -> float:
        """Tiempo interno de simulación."""

        return self._time_s

    @property
    def reactivity(self) -> float:
        """Reactividad actual."""

        return self._reactivity

    @property
    def neutron_population(self) -> float:
        """Población neutrónica actual."""

        return self._neutron_population

    @property
    def precursor_population(self) -> float:
        """Población de precursores actual."""

        return self._precursor_population