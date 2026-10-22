# Proyecto Nuclear

Simulación y monitorización de una central nuclear desarrollada en Python, orientada al estudio de sistemas de generación nuclear, dinámica de reactor, sistemas térmicos, instrumentación, seguridad y arquitectura IT/OT.

El proyecto forma parte del desarrollo del **TFG de ASIR (Administración de Sistemas Informáticos en Red)** y está planteado como una base sobre la que integrar posteriormente una arquitectura de monitorización y seguridad para entornos industriales y críticos.

---

## Descripción

El objetivo del proyecto es desarrollar una simulación modular de una central nuclear capaz de representar diferentes subsistemas de la planta y su interacción.

La arquitectura se ha diseñado de forma progresiva, separando el **motor físico de simulación**, los sistemas de control, la instrumentación y las futuras capas de supervisión y ciberseguridad.

Actualmente el proyecto incluye modelos para:

- Dinámica y potencia del reactor.
- Cinética puntual de neutrones.
- Reactividad.
- Retroalimentación por temperatura.
- Modelo térmico.
- Balance energético.
- Circuito térmico y conversión de energía térmica en eléctrica.
- Generador y turbina.
- Intercambiadores de calor.
- Condensador.
- Bombas.
- Instrumentación y sensores.
- Actuadores.
- Sistemas de seguridad.
- Alarmas.
- SCRAM.
- Control automático de potencia.
- Simulación de estados y evolución temporal de la planta.

---

## Arquitectura

El proyecto sigue una arquitectura modular dividida en diferentes capas:

```text
                    ┌───────────────────────┐
                    │     SCADA / Web       │
                    │       (futuro)        │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │ Monitorización /      │
                    │ Instrumentación       │
                    └───────────┬───────────┘
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
      ┌───────▼────────┐                 ┌────────▼───────┐
      │ Control de     │                 │ Sistema de     │
      │ planta         │                 │ seguridad      │
      └───────┬────────┘                 └────────┬───────┘
              │                                   │
              └─────────────────┬─────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │ PlantSimulation       │
                    └───────────┬───────────┘
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
      ┌───────▼────────┐                 ┌────────▼───────┐
      │ Reactor        │                 │ Sistema        │
      │ Dynamics       │                 │ térmico        │
      └───────┬────────┘                 └────────┬───────┘
              │                                   │
      ┌───────▼────────┐                 ┌────────▼───────┐
      │ Point Kinetics │                 │ Power Cycle    │
      └────────────────┘                 └────────────────┘
```

La separación entre módulos permite modificar o ampliar cada subsistema sin tener que reconstruir el resto de la aplicación.

---

## Reactor y cinética nuclear

El núcleo de la simulación utiliza un modelo de **cinética puntual de neutrones** con neutrones retardados.

El modelo implementa la evolución temporal de la población neutrónica y de los precursores de neutrones retardados:

```text
dn/dt = ((ρ - β) / Λ)n + λC

dC/dt = (β / Λ)n - λC
```

La integración temporal se realiza mediante un esquema **Runge-Kutta de cuarto orden (RK4)** con subpasos.

Sobre este modelo se construyen:

- `PointKinetics`
- `Reactivity`
- `TemperatureFeedback`
- `ReactorKinetics`
- `ReactorDynamics`

El sistema permite representar cambios de reactividad, respuesta de potencia y efectos de retroalimentación térmica.

---

## Control del reactor

El proyecto incorpora un controlador proporcional para regular la potencia del reactor respecto a un objetivo.

El controlador calcula el error entre la potencia objetivo y la potencia actual:

```text
error = potencia_objetivo - potencia_actual
```

y genera una reactividad de control limitada dentro de unos márgenes definidos.

También se integra con el sistema de dinámica del reactor para modificar la reactividad durante la simulación.

---

## Sistemas térmicos

La simulación incluye diferentes componentes relacionados con la transformación y transferencia de energía:

- Refrigerante.
- Transferencia de calor.
- Presión.
- Generador de vapor.
- Turbina.
- Generador eléctrico.
- Intercambiadores de calor.
- Condensador.
- Bombas.
- Pérdidas térmicas.
- Balance energético.
- Ciclo de potencia.

La finalidad es representar la cadena general:

```text
Reactor
   ↓
Energía térmica
   ↓
Refrigerante / circuito térmico
   ↓
Generador de vapor
   ↓
Turbina
   ↓
Generador
   ↓
Energía eléctrica
```

---

## Instrumentación

La planta dispone de una capa de instrumentación que permite representar sensores y actuadores.

Los sensores proporcionan información sobre variables de la planta y los actuadores permiten modificar determinados elementos del sistema.

Esta capa sirve como punto de separación entre los modelos físicos y las futuras capas de supervisión y control.

---

## Seguridad

Se ha desarrollado un sistema de seguridad compuesto por diferentes niveles:

- Límites de seguridad.
- Alarmas.
- Controlador de seguridad.
- Sistema de emergencia.
- Integración con la planta.
- SCRAM.

El **SCRAM** permite realizar una parada rápida del reactor cuando se detectan determinadas condiciones de seguridad.

La arquitectura está preparada para ampliar posteriormente los mecanismos de seguridad y representar escenarios de fallo más complejos.

---

## Testing

El proyecto utiliza `pytest` para verificar el funcionamiento de los diferentes módulos.

Actualmente la suite contiene **457 tests**, todos ellos pasando correctamente.

Última ejecución:

```text
457 passed
Tiempo aproximado: 13 segundos
```

Los tests cubren, entre otros:

- Reactor.
- Cinética puntual.
- Dinámica del reactor.
- Reactividad.
- Modelo térmico.
- Instrumentación.
- Actuadores.
- Sistemas de seguridad.
- SCRAM.
- Control de potencia.
- Simulación completa de planta.
- Evolución dinámica del reactor.

La suite de tests se utiliza como mecanismo de validación durante el desarrollo para detectar regresiones al añadir nuevos subsistemas.

---

## Estructura del proyecto

```text
Proyecto-Nuclear/
│
├── config/
│   └── Configuración del proyecto
│
├── data/
│   └── Datos utilizados por la simulación
│
├── docs/
│   └── Documentación técnica
│
├── scripts/
│   └── Scripts auxiliares
│
├── src/
│   └── nuclear_sim/
│       ├── plant/
│       └── ...
│
├── tests/
│   └── Tests automatizados
│
├── .gitignore
├── pyproject.toml
└── README.md
```

---

## Tecnologías

### Lenguaje

- Python 3

### Testing

- pytest

### Desarrollo

- Git
- GitHub
- Entorno virtual de Python

### Tecnologías previstas

El proyecto está planteado para incorporar progresivamente tecnologías relacionadas con:

- Flask.
- Bases de datos.
- SCADA.
- Monitorización.
- Wazuh.
- Seguridad IT/OT.
- Sistemas industriales.
- Registro y análisis de eventos.

---

## Roadmap

El desarrollo se realiza de forma incremental.

### Implementado

- [x] Modelo del reactor.
- [x] Cinética puntual.
- [x] Reactividad.
- [x] Retroalimentación térmica.
- [x] Dinámica del reactor.
- [x] Modelo térmico.
- [x] Ciclo de potencia.
- [x] Instrumentación.
- [x] Actuadores.
- [x] Sistemas de seguridad.
- [x] Alarmas.
- [x] SCRAM.
- [x] Control automático de potencia.
- [x] Simulación integrada.
- [x] Suite de tests automatizados.

### En desarrollo / previsto

- [ ] Persistencia de datos.
- [ ] Interfaz SCADA.
- [ ] Monitorización web.
- [ ] Integración con Wazuh.
- [ ] Detección de anomalías.
- [ ] Simulación de fallos e incidentes.
- [ ] Escenarios de ciberseguridad IT/OT.
- [ ] Despliegue de alta disponibilidad.
- [ ] Documentación final del TFG.

---

## Objetivos del proyecto

El proyecto tiene dos objetivos principales.

### Objetivo académico

Desarrollar una simulación modular de una planta nuclear que permita estudiar la interacción entre los diferentes sistemas físicos y de control.

### Objetivo de sistemas y ciberseguridad

Construir sobre la simulación una arquitectura que permita estudiar la **monitorización y seguridad de sistemas IT/OT en infraestructuras críticas**, utilizando la planta simulada como entorno de laboratorio.

Esto permitirá posteriormente experimentar con:

```text
Sistema físico simulado
        ↓
PLC / Control
        ↓
SCADA
        ↓
Red OT
        ↓
Monitorización
        ↓
Detección de anomalías
        ↓
SIEM / Wazuh
```

---

## Estado actual

El núcleo de simulación y los principales sistemas de control y seguridad se encuentran implementados y cubiertos mediante tests automatizados.

**Estado actual de la suite:**

```text
457 / 457 tests passing
```

El desarrollo continuará ampliando la simulación hacia las capas de **SCADA, monitorización, bases de datos y ciberseguridad IT/OT**.

---

## Aviso

Este proyecto es una **simulación educativa y de investigación**. No representa un sistema de control nuclear real ni debe utilizarse para operar, controlar o tomar decisiones sobre instalaciones nucleares reales.