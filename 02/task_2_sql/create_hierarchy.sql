CREATE OR REPLACE VIEW task_02.bom_hierarchy AS

WITH RECURSIVE

-- 1. One production quantity per material / month

monthly_materials AS (
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

-- 2. Annual production quantity

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

-- 3. Annual material -> component relationships

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
),

-- 4. Recursive BoM explosion

bom_tree AS (

    -- --------------------------------------------------------
    -- ANCHOR
    -- FIN -> first PROD -> its components
    -- --------------------------------------------------------

    SELECT
        fin_edge.plant_id AS plant,

        fin_mat.produced_material AS fin_material_id,
        fin_mat.produced_material_release_type
            AS fin_material_release_type,
        fin_mat.produced_material_production_type
            AS fin_material_production_type,
        fin_mat.produced_material_quantity
            AS fin_production_quantity,

        prod_edge.produced_material AS prod_material_id,
        prod_edge.produced_material_release_type
            AS prod_material_release_type,
        prod_edge.produced_material_production_type
            AS prod_material_production_type,
        prod_mat.produced_material_quantity
            AS prod_material_production_quantity,

        prod_edge.component_material AS component_id,
        prod_edge.component_material_release_type
            AS component_material_release_type,
        prod_edge.component_material_production_type
            AS component_material_production_type,
        prod_edge.component_material_quantity
            AS component_consumption_quantity,

        fin_edge.year,

        ARRAY[
            fin_mat.produced_material,
            prod_edge.produced_material,
            prod_edge.component_material
        ]::TEXT[] AS path

    FROM annual_edges AS fin_edge

    JOIN annual_materials AS fin_mat
        ON fin_mat.plant_id = fin_edge.plant_id
        AND fin_mat.year = fin_edge.year
        AND fin_mat.produced_material = fin_edge.produced_material

    -- FIN component becomes the first produced material
    JOIN annual_edges AS prod_edge
        ON prod_edge.plant_id = fin_edge.plant_id
        AND prod_edge.year = fin_edge.year
        AND prod_edge.produced_material =
            fin_edge.component_material

    JOIN annual_materials AS prod_mat
        ON prod_mat.plant_id = prod_edge.plant_id
        AND prod_mat.year = prod_edge.year
        AND prod_mat.produced_material =
            prod_edge.produced_material

    WHERE fin_edge.produced_material_release_type = 'FIN'


    UNION ALL


    -- --------------------------------------------------------
    -- RECURSIVE PART
    -- previous component -> next produced material
    -- --------------------------------------------------------

    SELECT
        tree.plant,

        tree.fin_material_id,
        tree.fin_material_release_type,
        tree.fin_material_production_type,
        tree.fin_production_quantity,

        next_edge.produced_material AS prod_material_id,
        next_edge.produced_material_release_type
            AS prod_material_release_type,
        next_edge.produced_material_production_type
            AS prod_material_production_type,
        next_mat.produced_material_quantity
            AS prod_material_production_quantity,

        next_edge.component_material AS component_id,
        next_edge.component_material_release_type
            AS component_material_release_type,
        next_edge.component_material_production_type
            AS component_material_production_type,
        next_edge.component_material_quantity
            AS component_consumption_quantity,

        tree.year,

        tree.path || next_edge.component_material

    FROM bom_tree AS tree

    JOIN annual_edges AS next_edge
        ON next_edge.plant_id = tree.plant
        AND next_edge.year = tree.year
        AND next_edge.produced_material =
            tree.component_id

    JOIN annual_materials AS next_mat
        ON next_mat.plant_id = next_edge.plant_id
        AND next_mat.year = next_edge.year
        AND next_mat.produced_material =
            next_edge.produced_material

    -- protection against cycles:
    -- A -> B -> C -> A
    WHERE NOT (
        next_edge.component_material = ANY(tree.path)
    )
)

-- ============================================================
-- 5. Final required dataset
-- ============================================================

SELECT
    plant,
    fin_material_id,
    fin_material_release_type,
    fin_material_production_type,
    fin_production_quantity,

    prod_material_id,
    prod_material_release_type,
    prod_material_production_type,
    prod_material_production_quantity,

    component_id,
    component_material_release_type,
    component_material_production_type,
    component_consumption_quantity,

    year

FROM bom_tree;