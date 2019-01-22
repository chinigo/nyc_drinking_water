from logzero import logger
import subprocess

from . import Base
from .. import projection

class Pipelines(Base):
    table_name = 'pipelines'
    data_file = './src/pipelines.sql'
    view_definiton = './src/derived_pipelines.sql'

    create_sql = """
        CREATE TABLE %s (
          id bigserial PRIMARY KEY,
          name varchar(100) NOT NULL,
          system varchar(100) NOT NULL,
          geom geometry(LineString, %s) NOT NULL,
          design_height geometry(LineString, %s) NULL DEFAULT NULL,
          surface_height geometry(LineString, %s) NULL DEFAULT NULL
        );
    """ % (table_name, projection.srid, projection.srid, projection.srid)

    index_sql = """
      CREATE INDEX %s_geom_idx ON %s USING GIST (geom);
      CREATE INDEX %s_design_height_idx ON %s USING GIST (design_height);
      CREATE INDEX %s_surface_height_idx ON %s USING GIST (surface_height);
    """ % (table_name, table_name, table_name, table_name, table_name, table_name)

    select_sql = """
      SELECT id, ST_AsEWKB(ST_Force3D(geom)) geom
      FROM pipelines
    """

    def _run(self):
        self._create_table()
        self._load_data()
        self._define_view()

    def _create_table(self):
        logger.info('Creating pipelines table.')

        if self.opts.force:
            self.db.cursor().execute('DROP TABLE IF EXISTS %s' % self.table_name)
        self.db.cursor().execute(self.create_sql)
        self.db.cursor().execute(self.index_sql)

    def _load_data(self):
        logger.info('Loading pipeline data.')

        sql = open(self.data_file, 'r')
        subprocess.call(['psql', 'ndw'], stdin=sql)
        sql.close()

    def _define_view(self):
        logger.info('Defining derived pipelines view.')
        sql = open(self.view_definiton, 'r')
        subprocess.call(['psql', 'ndw'], stdin=sql)
        sql.close()
