WITH monthly_materials AS (
    SELECT
        plant_id,
        year,
        month,
        produced_material,
        produced_material_release_type,
        produced_material_production_type,
        MAX(produced_material_quantity) AS produced_material_quantity
    FROM task_02.bom_raw
    GROUP BY
        plant_id,
        year,
        month,
        produced_material,
        produced_material_release_type,
        produced_material_production_type
),

annual_materials AS (
    SELECT
        plant_id,
        year,
        produced_material,
        produced_material_release_type,
        produced_material_production_type,
        SUM(produced_material_quantity) AS produced_material_quantity
    FROM monthly_materials
    GROUP BY
        plant_id,
        year,
        produced_material,
        produced_material_release_type,
        produced_material_production_type
),

annual_edges AS (
    SELECT
        plant_id,
        year,
        produced_material,
        produced_material_release_type,
        produced_material_production_type,
        component_material,
        component_material_release_type,
        component_material_production_type,
        SUM(component_material_quantity) AS component_material_quantity
    FROM task_02.bom_raw
    GROUP BY
        plant_id,
        year,
        produced_material,
        produced_material_release_type,
        produced_material_production_type,
        component_material,
        component_material_release_type,
        component_material_production_type
)

SELECT *
-- FROM annual_materials
 FROM annual_edges
LIMIT 100;