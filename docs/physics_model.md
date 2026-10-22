# Modelo físico

El simulador separa los modelos de planta de los modelos físicos avanzados. Las
clases sencillas siguen siendo útiles para SCADA y control, mientras que los
módulos físicos permiten estudiar las ecuaciones que hay detrás.

## Decaimiento radiactivo

Para un radionúclido:

`N(t) = N0 exp(-lambda t)`

`lambda = ln(2) / T_1/2`

`A(t) = lambda N(t)`

La energía acumulada ideal de una rama puede calcularse como:

`E = N_decays E_decay`

con la conversión `1 MeV = 1.602176634e-13 J`.

## Balance térmico

Para un fluido con propiedades constantes:

`Q = m c_p Delta T`

y para una potencia térmica:

`Q_dot = m_dot c_p Delta T`

La convección se modela mediante:

`Q_dot = h A Delta T`

El intercambiador incorpora la diferencia logarítmica de temperaturas:

`Q_dot = U A Delta T_lm`

`Delta T_lm = (Delta T1 - Delta T2) / ln(Delta T1 / Delta T2)`

## Radiación

Para una fuente puntual isotrópica idealizada, la intensidad geométrica sigue:

`I(r) proportional 1 / (4 pi r^2)`

La atenuación exponencial sin dispersión múltiple ni buildup es:

`I(x) = I0 exp(-mu x)`

## Dosis

La dosis absorbida es:

`D = E_abs / m`

con unidades Gy = J/kg.

Una forma simplificada de dosis equivalente es:

`H = w_R D`

con `w_R` como factor de ponderación radiológica.

## Cinética puntual

El módulo `PointKinetics` implementa un grupo de neutrones retardados:

`dn/dt = ((rho-beta)/Lambda)n + lambda_d C`

`dC/dt = (beta/Lambda)n - lambda_d C`

Aquí `rho` es la reactividad, `beta` la fracción efectiva de neutrones
retardados, `Lambda` el tiempo de generación de neutrones y `C` la concentración
de precursores.

Este modelo es una aproximación de cinética puntual. No sustituye a un cálculo
espacial de transporte como OpenMC.
