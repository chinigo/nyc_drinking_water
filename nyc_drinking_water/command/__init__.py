from nyc_drinking_water.grass_wrapper import GrassWrapper
from logzero import logger
import psycopg2
from psycopg2.extras import LoggingConnection

__all__ = ['run_all', 'ensure_postgis', 'ingest_dem', 'hillshade', 'basins', 'reservoirs', 'watersheds', 'pipelines']


class Base(object):
    def __init__(self, opts):
        self.opts = opts

        self.db = psycopg2.connect(self.opts.connection, connection_factory=LoggingConnection)
        self.db.initialize(logger)
        self.db.set_session(autocommit=True)


    def run(self):
        self.grass = GrassWrapper(self.opts)

        if self.opts.force: self._drop_table()
        self._create_table()

        self._run()
        self._clean_grass()

    def _drop_table(self):
        self.db.cursor().execute("DROP TABLE IF EXISTS %s" % self.table_name)

    def _create_table(self):
        logger.info('Creating %s table' % self.table_name)
        self.db.cursor().execute(self.create_sql)

    def _clean_grass(self):
        self.grass = None
        self.grass.run_command('g.remove', type='raster', pattern='tmp_*', flags='f')
        self.grass.run_command('g.remove', type='vect', pattern='tmp_*', flags='f')
