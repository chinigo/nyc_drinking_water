from logzero import logger

from . import Base
from .ingest_dem import output_layer as input_layer

output_layer = 'relief'

class Hillshade(Base):
    def _run(self):
        logger.info('Calculating shaded relief map.')
        self.grass.run_command('r.relief',
                input=input_layer,
                output=output_layer,
                zscale='2')
