from nyc_drinking_water.grass_wrapper import GrassWrapper

__all__ = ['ingest_dem', 'hillshade', 'basins', 'reservoirs', 'watersheds']


class Base(object):
    def __init__(self, opts):
        self.opts = opts

    def run(self):
        self.grass = GrassWrapper(self.opts)
        self._run()
        self.grass = None
