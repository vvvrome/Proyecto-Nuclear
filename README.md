# Proyecto Nuclear

Simulador web de una planta nuclear desarrollado como proyecto de TFG para **ASIR + Física**.

El proyecto combina una simulación simplificada de la dinámica de un reactor nuclear con una infraestructura de servidor Linux, base de datos, aplicación web y medidas de administración y seguridad propias de un entorno ASIR.

---

## 1. Descripción

El objetivo del proyecto es desarrollar una plataforma capaz de representar el comportamiento simplificado de una planta nuclear y permitir al usuario interactuar con diferentes parámetros de operación.

La aplicación integra:

- Simulación neutrónica mediante **OpenMC**.
- Modelo simplificado de cinética puntual del reactor.
- Modelo térmico.
- Modelo del ciclo de potencia.
- Telemetría de la simulación.
- Gestión de incidentes y estados de seguridad.
- Persistencia de datos mediante **MySQL**.
- Aplicación web desarrollada con **Flask**.
- Servidor de aplicación **Gunicorn**.
- Gestión del servicio mediante **systemd**.
- Administración de un servidor **Ubuntu Server**.
- Configuración de red y firewall mediante **UFW**.
- Pruebas automatizadas.

El proyecto se está desarrollando además con una orientación específica hacia los módulos de **ASIR**, de forma que la infraestructura necesaria para ejecutar la aplicación forme parte del propio TFG.

---

# 2. Arquitectura general

La arquitectura actual puede resumirse de la siguiente forma:

```text
                         ┌─────────────────────┐
                         │     Usuario         │
                         │   Navegador web     │
                         └──────────┬──────────┘
                                    │
                                    │ HTTP :5000
                                    ▼
                         ┌─────────────────────┐
                         │      Gunicorn       │
                         │    1 worker         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       Flask         │
                         │      Dashboard      │
                         └──────────┬──────────┘
                                    │
                   ┌────────────────┼────────────────┐
                   │                │                │
                   ▼                ▼                ▼
          ┌────────────────┐ ┌──────────────┐ ┌──────────────┐
          │ PlantSimulation│ │   OpenMC     │ │    MySQL     │
          │                │ │              │ │              │
          │ Reactor        │ │ Neutronics   │ │ Simulations  │
          │ Thermal        │ │ Statepoints  │ │ Telemetry    │
          │ Power cycle    │ │              │ │ Incidents    │
          └────────────────┘ └──────────────┘ └──────────────┘
```

La aplicación se ejecuta actualmente como un servicio `systemd` denominado:

```text
nuclear-sim.service
```

---

# 3. Tecnologías

## Software

- Ubuntu Server
- Python 3.12+
- OpenMC 0.16.0
- Flask
- Gunicorn
- MySQL
- systemd
- UFW
- Git / GitHub

## Librerías principales

- NumPy
- SciPy
- Matplotlib
- Pandas
- MySQL Connector/Python
- Flask
- Pytest

---

# 4. Estructura del proyecto

La aplicación utiliza una estructura basada en paquetes Python dentro de `src/`:

```text
Proyecto-Nuclear/
├── src/
│   └── nuclear_sim/
│       ├── database/
│       ├── incidents/
│       ├── plant/
│       ├── reactor/
│       ├── telemetry/
│       ├── thermal/
│       ├── web/
│       └── ...
│
├── tests/
├── data/
├── pyproject.toml
├── README.md
└── ...
```

La separación por módulos permite mantener independientes la simulación física, la persistencia de datos, la telemetría y la aplicación web.

---

# 5. Simulación nuclear

## OpenMC

OpenMC se utiliza para realizar los cálculos neutrónicos del modelo.

Actualmente se dispone de un modelo simplificado de un elemento de combustible tipo PWR que incluye:

- Combustible UO₂.
- Helio como material del gap.
- Zircaloy-4 como revestimiento.
- Agua ligera como moderador/refrigerante.

Los materiales y parámetros principales se encuentran dentro del paquete:

```text
src/nuclear_sim/reactor/
```

La simulación genera un `statepoint` de OpenMC que posteriormente se procesa para obtener información como:

- `keff`
- desviación estándar de `keff`
- número de batches
- número de partículas

Los resultados de OpenMC pueden almacenarse asociados a una ejecución concreta de la simulación.

> **Nota:** el modelo neutrónico actual es un modelo simplificado orientado al desarrollo académico del proyecto. No pretende representar con precisión una central nuclear comercial completa.

---

# 6. Dinámica del reactor

La simulación incorpora un modelo simplificado de dinámica del reactor basado en:

- Potencia del reactor.
- Reactividad.
- Temperatura.
- Retroalimentación por temperatura.
- Calor eliminado.
- Reactividad externa.
- Cinética puntual.

El usuario puede modificar desde el dashboard parámetros como:

```text
dt_s
heat_removed_mw
external_reactivity
```

Por ejemplo, una reactividad positiva produce un aumento de potencia, mientras que una reactividad negativa produce una reducción.

El sistema también permite reiniciar la simulación desde la interfaz web.

---

# 7. Modelo térmico

El modelo térmico utiliza una temperatura inicial de:

```text
573.15 K
```

y una capacidad térmica definida en el modelo.

La evolución de la temperatura depende de la relación entre:

```text
potencia térmica generada
        -
calor eliminado
```

El modelo incluye además retroalimentación de temperatura sobre la reactividad del reactor.

---

# 8. Dashboard web

La aplicación dispone de un dashboard web desarrollado con Flask.

Actualmente permite:

- Consultar el estado de la simulación.
- Ejecutar pasos de simulación.
- Modificar la reactividad externa.
- Modificar el calor eliminado.
- Modificar el intervalo temporal.
- Reiniciar la simulación.
- Consultar resultados de OpenMC.
- Visualizar la evolución de la potencia mediante una gráfica.
- Consultar telemetría mediante una API interna.

La interfaz mantiene los valores introducidos por el usuario después de ejecutar un paso, evitando que los parámetros vuelvan a sus valores predeterminados en cada petición.

---

# 9. Telemetría

La simulación dispone de un sistema de recopilación de telemetría.

Se almacenan diferentes variables asociadas al estado de la planta, incluyendo información relacionada con:

- Tiempo.
- Potencia.
- Reactividad.
- Temperatura.
- Variables térmicas.
- Estado del reactor.

La aplicación web expone la telemetría mediante:

```text
GET /simulation/telemetry
```

La información se utiliza actualmente para representar la evolución de la potencia en el dashboard.

---

# 10. Base de datos

El proyecto utiliza **MySQL** para almacenar información persistente.

La base de datos utilizada es:

```text
nuclear_sim
```

Entre las tablas utilizadas se encuentran:

```text
simulation_runs
telemetry_readings
incidents
openmc_results
```

## `simulation_runs`

Registra las ejecuciones de la simulación.

Incluye información como:

- Identificador.
- Fecha de inicio.
- Fecha de finalización.
- Descripción.
- Potencia inicial.
- Estado.

## `telemetry_readings`

Almacena las lecturas de telemetría asociadas a una ejecución.

## `incidents`

Permite registrar incidentes de la simulación.

## `openmc_results`

Almacena los resultados de OpenMC asociados a una ejecución:

- Ruta del statepoint.
- `keff`.
- Desviación estándar.
- Batches.
- Partículas.
- Fecha de creación.

Los resultados de OpenMC están relacionados con `simulation_runs` mediante una clave foránea.

---

# 11. Configuración de la base de datos

La aplicación no contiene directamente las credenciales de MySQL dentro del código.

La configuración se obtiene mediante variables de entorno:

```text
MYSQL_HOST
MYSQL_PORT
MYSQL_USER
MYSQL_DATABASE
MYSQL_PASSWORD
```

Estas variables se almacenan en un archivo externo:

```text
~/.nuclear_sim_env
```

El archivo está protegido mediante permisos restrictivos para que únicamente su propietario pueda leerlo y modificarlo.

El servicio `systemd` utiliza este archivo mediante:

```text
EnvironmentFile=/home/vvvrome/.nuclear_sim_env
```

Esto permite separar las credenciales de la aplicación y evitar almacenarlas directamente en el código fuente.

---

# 12. Servicio systemd

La aplicación se ejecuta como un servicio de sistema:

```text
nuclear-sim.service
```

El servicio utiliza Gunicorn como servidor de aplicación.

Características actuales:

```text
User=vvvrome
Group=vvvrome
Workers=1
Bind=0.0.0.0:5000
Restart=on-failure
RestartSec=5
```

El servicio está configurado para iniciarse automáticamente con el sistema:

```text
WantedBy=multi-user.target
```

También existe una dependencia con MySQL y la red.

El uso de un único worker se mantiene actualmente porque el estado de la simulación se encuentra en memoria. Utilizar varios workers sin implementar un mecanismo de estado compartido podría generar diferentes estados de simulación entre procesos.

---

# 13. Recuperación automática

El servicio está configurado con:

```text
Restart=on-failure
RestartSec=5
```

Se realizó una prueba controlada terminando el proceso principal de Gunicorn.

El comportamiento observado fue:

```text
Proceso principal
      ↓
SIGKILL
      ↓
systemd detecta el fallo
      ↓
servicio marcado como fallido
      ↓
reinicio automático
      ↓
nuevo proceso Gunicorn
      ↓
servicio activo
      ↓
HTTP 200 OK
```

Esto demuestra la capacidad básica de recuperación automática del servicio.

---

# 14. Red

El servidor utiliza actualmente la interfaz:

```text
ens33
```

con una dirección IPv4 dentro de la red:

```text
192.168.176.0/24
```

La aplicación está disponible actualmente mediante:

```text
http://192.168.176.133:5000/
```

Los servicios principales identificados son:

```text
22/tcp      SSH
3306/tcp    MySQL
5000/tcp    Gunicorn
```

MySQL está configurado para escuchar únicamente en:

```text
127.0.0.1:3306
```

por lo que la base de datos no está directamente expuesta a la red.

---

# 15. Firewall

El servidor utiliza **UFW**.

La política actual es:

```text
Default: deny incoming
Default: allow outgoing
```

Las reglas de entrada actuales permiten:

```text
22/tcp    desde 192.168.176.0/24
5000/tcp  desde 192.168.176.0/24
```

De esta forma, el acceso SSH y la aplicación web están limitados a la red utilizada para el proyecto.

El funcionamiento se comprobó desde el equipo cliente después de activar el firewall.

---

# 16. Recursos del servidor

La máquina virtual utilizada para el proyecto dispone actualmente de:

```text
CPU:       4 núcleos
RAM:       7.2 GiB
Swap:      4 GiB
Disco:     146 GB
```

En una medición realizada durante el desarrollo:

```text
RAM disponible: 6.1 GiB
Disco utilizado: 63 GB
Disco disponible: 76 GB
Swap utilizada: 0 B
```

Estos datos servirán posteriormente como línea base para estudiar el consumo de recursos de la aplicación y de las simulaciones OpenMC.

---

# 17. Pruebas

El proyecto dispone de una batería de pruebas automatizadas mediante **Pytest**.

Actualmente:

```text
591 tests passed
```

Las pruebas cubren diferentes partes del sistema, incluyendo:

- Modelos físicos.
- Dinámica del reactor.
- Modelo térmico.
- Telemetría.
- Persistencia en MySQL.
- Resultados OpenMC.
- Integración de diferentes componentes.

Además de las pruebas automatizadas, se han realizado pruebas manuales de:

- Ejecución de OpenMC.
- Persistencia de resultados.
- Funcionamiento del dashboard.
- Reinicio de la simulación.
- Recuperación automática del servicio.
- Acceso HTTP.
- Acceso SSH.
- Funcionamiento del firewall.

---

# 18. ASIR

El proyecto está diseñado para integrar diferentes contenidos del ciclo de **Administración de Sistemas Informáticos en Red**.

## ASO

Trabajo realizado o en desarrollo:

- Administración de Ubuntu Server.
- Usuarios y grupos.
- Permisos.
- Procesos.
- systemd.
- Gunicorn.
- Variables de entorno.
- Logs.
- Monitorización de recursos.
- Recuperación automática de servicios.

## SRI

Trabajo realizado o en desarrollo:

- Configuración de red.
- Direccionamiento IPv4.
- SSH.
- Identificación de puertos.
- UFW.
- Restricción de tráfico entrante.
- Análisis de servicios de red.

## IAW

Trabajo realizado o previsto:

- Flask.
- Gunicorn.
- Aplicación web.
- Configuración de servidor web.
- Nginx.
- HTTPS.
- Publicación de la aplicación en producción.

## ASGB

Trabajo realizado o previsto:

- MySQL.
- Creación de base de datos.
- Usuarios de base de datos.
- Privilegios.
- Integridad referencial.
- Persistencia de simulaciones.
- Telemetría.
- Resultados OpenMC.
- Copias de seguridad.

## SAD

Trabajo realizado o previsto:

- Disponibilidad del servicio.
- Recuperación automática.
- Copias de seguridad.
- Recuperación ante fallos.
- Mantenimiento del servidor.
- Hardening.

## Sostenibilidad

Trabajo previsto:

- Análisis de consumo de CPU.
- Análisis de memoria.
- Uso de almacenamiento.
- Optimización de simulaciones.
- Gestión de resultados OpenMC.
- Reducción de recursos innecesarios.

## Ciberseguridad

Trabajo realizado o previsto:

- Firewall.
- Restricción de servicios.
- Protección de credenciales.
- Ejecución de servicios sin privilegios de root.
- Hardening de SSH.
- Auditoría y logs.
- Monitorización.
- Detección de eventos.
- Medidas de seguridad adicionales.

---

# 19. Instalación

## Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd Proyecto-Nuclear
```

## Crear el entorno

El proyecto utiliza un entorno Python con OpenMC.

Una vez disponible el entorno:

```bash
python --version
openmc --version
```

## Instalar el proyecto

```bash
pip install -e .
```

Para instalar las dependencias de desarrollo:

```bash
pip install -e ".[dev]"
```

---

# 20. Configuración de MySQL

Crear la base de datos:

```sql
CREATE DATABASE nuclear_sim;
```

Crear el usuario de aplicación y conceder únicamente los permisos necesarios.

Las credenciales deben configurarse mediante variables de entorno y no deben incluirse en Git.

Ejemplo conceptual:

```text
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=nuclear_sim
MYSQL_DATABASE=nuclear_sim
MYSQL_PASSWORD=<CONTRASEÑA>
```

El archivo utilizado para estas variables debe mantenerse fuera del repositorio.

---

# 21. Ejecutar las pruebas

Desde el entorno Python:

```bash
pytest -q
```

El estado actual del proyecto es:

```text
591 tests passed
```

---

# 22. Ejecutar la aplicación

En desarrollo se puede ejecutar la aplicación Flask mediante el entorno Python.

En el servidor de producción del proyecto se utiliza actualmente:

```text
systemd
    ↓
Gunicorn
    ↓
Flask
```

El servicio se gestiona mediante:

```bash
sudo systemctl start nuclear-sim
sudo systemctl stop nuclear-sim
sudo systemctl restart nuclear-sim
sudo systemctl status nuclear-sim
```

Para consultar los logs:

```bash
sudo journalctl -u nuclear-sim
```

---

# 23. OpenMC

La ejecución de OpenMC se realiza mediante el entorno preparado para la simulación.

Los resultados generan archivos `statepoint` que son procesados posteriormente por la aplicación.

Los archivos de datos de OpenMC y resultados generados no deben incorporarse innecesariamente al repositorio Git debido a su tamaño.

---

# 24. Control de versiones

El proyecto utiliza Git para controlar la evolución del código.

Los cambios importantes se almacenan mediante commits y se sincronizan con GitHub.

Ejemplo:

```bash
git status
git add .
git commit -m "Descripción del cambio"
git push
```

Los archivos sensibles, credenciales y datos generados que no deben formar parte del repositorio están excluidos mediante `.gitignore`.

---

# 25. Estado actual

Actualmente el proyecto cuenta con:

- [x] Modelo de materiales OpenMC.
- [x] Geometría simplificada del reactor.
- [x] Configuración de OpenMC.
- [x] Ejecución de OpenMC.
- [x] Lectura de statepoints.
- [x] Modelo de cinética puntual.
- [x] Modelo térmico.
- [x] Modelo de ciclo de potencia.
- [x] Telemetría.
- [x] Gestión de incidentes.
- [x] Persistencia MySQL.
- [x] Persistencia de resultados OpenMC.
- [x] Dashboard Flask.
- [x] Gráfica de potencia.
- [x] Reinicio de simulación.
- [x] Persistencia de parámetros del formulario.
- [x] Gunicorn.
- [x] Servicio systemd.
- [x] Variables de entorno protegidas.
- [x] Logs mediante journalctl.
- [x] Recuperación automática del servicio.
- [x] Firewall UFW.
- [x] Restricción de puertos.
- [x] Pruebas automatizadas.
- [x] 591 tests superados.

### Próximos pasos

- [ ] Endurecimiento de SSH.
- [ ] Configuración de Nginx.
- [ ] HTTPS.
- [ ] Gestión avanzada de MySQL.
- [ ] Sistema de copias de seguridad.
- [ ] Recuperación y pruebas de backup.
- [ ] Monitorización avanzada.
- [ ] Auditoría y ciberseguridad.
- [ ] Optimización de recursos.
- [ ] Documentación completa del TFG.

---

# 26. Objetivo final

El objetivo final del proyecto es disponer de una plataforma que combine:

```text
Física nuclear
      +
Simulación OpenMC
      +
Programación Python
      +
Base de datos
      +
Aplicación web
      +
Administración Linux
      +
Redes
      +
Seguridad
      +
Monitorización
      +
Sostenibilidad
```

De esta forma, el proyecto no se limita a desarrollar una aplicación, sino que integra la aplicación con la infraestructura necesaria para desplegarla, administrarla, protegerla y mantenerla en funcionamiento.

---

## Autor

Proyecto desarrollado como **TFG de ASIR + Física**.

Repositorio:  https://github/vvvrome/Proyecto-Nuclear

```text
GitHub: <URL_DEL_REPOSITORIO>
```
