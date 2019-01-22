from grass.script import core as gscript
from logzero import logger

from . import projection, HiddenPrints
with HiddenPrints(): from grass_session import Session


gisdb='grass_session'
location='new_york'

class GrassWrapper(object):
    def __init__(self, opts):
        self.opts = opts

        if self.opts.verbose:
            gscript._debug_level = 5

        self._open_session()
        self.run_command('g.proj', proj4=projection.proj4, flags='c')

    def run_command(self, command, **kwargs):
        kwargs.update(
                overwrite=self.opts.force,
                verbose=self.opts.verbose)

        return gscript.run_command(command, **kwargs)

    def list_pairs(self, *args, **kwargs):
        return gscript.list_pairs(*args, **kwargs)

    def _open_session(self):
        self.session = Session()
        self.session.open(gisdb=gisdb, location=location, create_opts='EPSG:4326')

    def __del__(self):
        self.session.close()
