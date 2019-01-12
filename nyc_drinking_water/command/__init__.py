from nyc_drinking_water.grass_wrapper import GrassWrapper
from logzero import logger
import psycopg2
from psycopg2.extras import LoggingConnection

__all__ = ['run_all', 'ingest_dem', 'hillshade', 'basins', 'reservoirs', 'watersheds']


class Base(object):
    def __init__(self, opts):
        self.opts = opts

        self.db = psycopg2.connect(self.opts.connection, connection_factory=LoggingConnection)
        self.db.initialize(logger)
        self.db.set_session(autocommit=True)


    def run(self):
        self.grass = GrassWrapper(self.opts)
        self._run()
        self.grass = None
