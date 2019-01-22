DROP MATERIALIZED VIEW IF EXISTS derived_pipelines;

CREATE MATERIALIZED VIEW derived_pipelines
AS WITH
/**
 * Add run length as M dimension along each pipeline.
 *
 * We ignore Z dimension because we're primarily interested in pipeline
 * gradient, which is defined as (vertical rise):(horizontal run).
 */
measured_pipelines AS (
  SELECT p.id,
    ST_AddMeasure(
      ST_Force3D(p.geom), -- TODO: Force 3D until we add pipeline depth data
      0,
      ST_Length2D(p.geom) -- Ignore Z dimension
    ) AS geom
  FROM pipelines AS p
),

/**
 * Calculate surface height and pipeline depth at each vertex.
 *
 * For each vertex, we look up the elevation from the DEM raster, and create
 * two copies.
 *
 * For one copy we substitute the elevation for the Z coordinate. These points
 * describe a line along the surface that tracks the pipelines beneath.
 *
 * For the other copy we substitute the depth of the pipeline for Z (defined as
 * elevation - pipeline depth). These points trace the pipeline's depth
 * relative to the surface (whereas the actual pipeline data is relative to sea
 * level).
 */
measured_vertices AS (
  SELECT pts.id,
    -- Surface elevation at vertex
    ST_MakePoint(
      ST_X(pts.geom),
      ST_Y(pts.geom),
      ST_Value(d.rast, pts.geom),
      ST_M(pts.geom)
    ) AS surface_point,

    -- Pipeline depth at vertex
    ST_MakePoint(
      ST_X(pts.geom),
      ST_Y(pts.geom),
      ST_Value(d.rast, pts.geom) - ST_Z(pts.geom),
      ST_M(pts.geom)
    ) AS depth_point,

    -- Remember elevations for design slope calculation later
    ST_Value(d.rast, pts.geom) AS elevation
  FROM (
    -- Blow LINESTRINGs out into XYZM point collection
    SELECT mp.id, (ST_DumpPoints(mp.geom)).geom AS geom
    FROM measured_pipelines AS mp
  ) AS pts
  INNER JOIN dem.dem AS d
    ON ST_Intersects(pts.geom, d.rast)
),

/**
 * Generate lines along the surface that track the pipelines beneath.
 *
 * Also hang onto the raw elevation values, which we'll need to calculate the
 * design slope in the next step. We rely on the (possibly undefined?) property
 * of array_agg() ordering its elements in the same way that ST_Collect() does.
 */
surface_lines AS (
  SELECT mv.id,
    array_agg(mv.elevation) AS elevations,
    ST_LineFromMultiPoint( ST_Collect(mv.surface_point) ) AS geom
  FROM measured_vertices AS mv
  GROUP BY mv.id
),

/**
 * Calculate the design slope for each pipeline.
 *
 * Design slope is the average slope between the first and last point.
 *
 * We want to linearly interpolate this to the Z coordinate of each vertex along
 * the pipeline, but because AddMeasure only modifies the M coordinate, we have
 * to swap them temporarily.
 */
design_slopes AS (
  SELECT sl.id,
    ST_SwapOrdinates(
      ST_AddMeasure(
        ST_SwapOrdinates(sl.geom, 'mz'), -- Stash the M coordinate in Z
        sl.elevations[1], -- Postgres arrays are 1-indexed lol!
        sl.elevations[ array_length(sl.elevations, 1) ]
      ),
      'mz' -- Restore Z and M coordinates
    ) AS geom
  FROM surface_lines sl
)

SELECT p.id,
  p.name,
  p.system,
  ST_SetSRID(mp.geom, 200100)  AS pipeline,
  ST_SetSRID(sl.geom, 200100)  AS surface_line,
  ST_SetSRID(ds.geom, 200100)  AS design_line

FROM pipelines AS p
INNER JOIN measured_pipelines AS mp
  ON p.id = mp.id
INNER JOIN surface_lines AS sl
  ON p.id = sl.id
INNER JOIN design_slopes AS ds
  ON p.id = ds.id
ORDER BY p.id ASC

WITH DATA
;

CREATE UNIQUE INDEX derived_pipelines_id_idx ON derived_pipelines;
CREATE INDEX derived_pipelines_pipeline_idx ON derived_pipelines USING GIST (pipeline);
CREATE INDEX derived_pipelines_surface_line_idx ON derived_pipelines USING GIST (surface_line);
CREATE INDEX derived_pipelines_design_line_idx ON derived_pipelines USING GIST (design_line);
