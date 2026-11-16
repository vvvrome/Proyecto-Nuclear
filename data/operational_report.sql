USE nuclear_sim;

DROP PROCEDURE IF EXISTS sp_simulation_report;

DELIMITER //

CREATE PROCEDURE sp_simulation_report(IN p_run_id INT)
BEGIN

    -- 1. Información general de la simulación
    SELECT
        sr.id,
        sr.started_at,
        sr.ended_at,
        sr.description,
        sr.initial_power_fraction,
        sr.status
    FROM simulation_runs AS sr
    WHERE sr.id = p_run_id;

    -- 2. Resultado OpenMC
    SELECT
        o.id,
        o.run_id,
        o.statepoint_path,
        o.keff,
        o.keff_std_dev,
        o.batches,
        o.particles,
        o.created_at
    FROM openmc_results AS o
    WHERE o.run_id = p_run_id;

    -- 3. Estadísticas de telemetría
    SELECT
        t.variable,
        t.unit,
        COUNT(*) AS readings,
        MIN(t.value) AS minimum_value,
        MAX(t.value) AS maximum_value,
        AVG(t.value) AS average_value
    FROM telemetry_readings AS t
    WHERE t.run_id = p_run_id
    GROUP BY t.variable, t.unit
    ORDER BY t.variable;

    -- 4. Incidentes de la simulación
    SELECT
        i.id,
        i.timestamp_s,
        i.name,
        i.severity,
        i.message,
        i.source,
        i.status
    FROM incidents AS i
    WHERE i.run_id = p_run_id
    ORDER BY i.timestamp_s;

END //

DELIMITER ;
