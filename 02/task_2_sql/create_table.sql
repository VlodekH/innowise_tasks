-- schema for second task
CREATE SCHEMA IF NOT EXISTS task_02;

DROP TABLE IF EXISTS task_02.bom_raw;

CREATE TABLE task_02.bom_raw (
    year INTEGER,
    month INTEGER,
    produced_material TEXT,
    produced_material_production_type INTEGER,
    produced_material_release_type TEXT,
    produced_material_quantity NUMERIC,
    component_material TEXT,
    component_material_production_type INTEGER,
    component_material_release_type TEXT,
    component_material_quantity NUMERIC,
    plant_id TEXT
);
