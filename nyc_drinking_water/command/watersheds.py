import re
from logzero import logger

from . import Base
from .reservoirs import Reservoirs, reservoirs
from .. import projection

class Watersheds(Base):
    table_name = 'watersheds'
    tmp_table_name = 'tmp_watersheds'

    create_sql = """
        CREATE TABLE %s (
          id bigserial PRIMARY KEY,
          reservoir_id bigint NOT NULL,
          geom geometry(MultiPolygon, %s) NOT NULL
        );
    """ % (table_name, projection.srid)

    cross_points_sql = """
        WITH buffered AS (
          SELECT ST_Buffer(
            ST_ConcaveHull(
              ST_SimplifyPreserveTopology(geom, 100),
              0.99,
              false
              ),
            100
            ) AS geom
          FROM %s
          WHERE name = %%s
        ),
        crosspoints AS (
          SELECT
            buffered.geom AS buffered_reservoir,
            ST_Intersection(streams.geom, ST_Boundary(buffered.geom)) AS point
          FROM buffered
          INNER JOIN streams ON ST_Intersects(buffered.geom, streams.geom)
        )

        SELECT
          ST_X((ST_Dump(crosspoints.point)).geom) AS x,
          ST_y((ST_Dump(crosspoints.point)).geom) AS y
        FROM crosspoints
        WHERE NOT ST_IsEmpty(crosspoints.point)
    """ % (Reservoirs.table_name)

    reservoir_id_sql = "SELECT id FROM %s WHERE name = %%s" % (Reservoirs.table_name)

    copy_watersheds_sql = """
      INSERT INTO %s (reservoir_id, geom)
      SELECT %%d, ST_SetSRID(ST_Multi(geom), %d)
      FROM %s
    """ % (table_name, projection.srid, tmp_table_name)

    def _run(self):
        self._calculate_watersheds()

    def _create_table(self):
        logger.info('Creating %s table' % self.table_name)
        self.db.cursor().execute(self.create_sql)

    def _calculate_watersheds(self):
        for reservoir in reservoirs:
            logger.info('Generating watershed for %s' % reservoir.output_name)

            cursor = self.db.cursor()
            cursor.execute(self.cross_points_sql, [reservoir.output_name])

            self._concatenate_subwatersheds(
                    reservoir,
                    self._calculate_subsheds(reservoir, cursor))
            self._export_watersheds(reservoir)

    def _calculate_subsheds(self, reservoir, cross_points):
        i = 0
        subsheds = []
        for (x, y) in cross_points.fetchall():
            logger.info('Generating sub-watershed for stream entering at (%f, %f)' % (x, y))

            self.grass.run_command('r.water.outlet',
                input='drainage',
                output='tmp_%s_%d' % (reservoir.sanitized_name, i),
                coordinates='%f,%f' % (x,y))
            subsheds.append('tmp_%s_%d' % (reservoir.sanitized_name, i))
            i = i+1

        return subsheds

    def _concatenate_subwatersheds(self, reservoir, subsheds):
        logger.info('Concatenating sub-watersheds.')

        joined_name = 'tmp_%s_rast' % reservoir.sanitized_name
        if len(subsheds) > 1:
            self.grass.run_command('r.patch',
                    input=','.join(subsheds),
                    output=joined_name)
        else:
            self.grass.run_command('g.copy', raster='%s,%s' % (subsheds[0],joined_name))

        self.grass.run_command('r.to.vect',
                type='area',
                input=joined_name,
                output='tmp_%s_rawvect' % reservoir.sanitized_name)

        self.grass.run_command('v.clean',
                type='area',
                input='tmp_%s_rawvect' % reservoir.sanitized_name,
                output='tmp_overall_%s' % reservoir.sanitized_name,
                threshold='2000',
                tool='rmarea')

    def _export_watersheds(self, reservoir):
        logger.info('Copying to PostGIS temp table.')
        self.grass.run_command('v.out.postgis',
                type='area',
                output='PG:dbname=ndw',
                output_layer=self.tmp_table_name,
                input='tmp_overall_%s' % reservoir.sanitized_name)

        logger.info('Copying to PostGIS permanent %s table.' % self.table_name)

        curs = self.db.cursor()
        curs.execute(self.reservoir_id_sql, [reservoir.output_name])
        reservoir_id = curs.fetchone()[0]

        self.db.cursor().execute(self.copy_watersheds_sql % reservoir_id)
