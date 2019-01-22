from logzero import logger

from . import Base
from .ingest_dem import output_layer as input_layer

output_drainage       = 'drainage'
output_basin          = 'basin'
output_stream         = 'streams'

tmp_basin             = 'tmp_basin'
tmp_clipped_elevation = 'tmp_clipped_elevation'
tmp_stream            = 'tmp_stream'
tmp_stream_thinned    = 'tmp_stream_thinned'

class Basins(Base):
    def _run(self):
        self._constrain_region()
        self._calculate_basins()
        self._vectorize_basins()
        self._thin_streams()
        self._vectorize_streams()
        self._clean_temp_files()

    def _constrain_region(self):
        logger.info('Constraining region.')
        self.grass.run_command('g.region',
                ewres='27.0218',
                nsres='27.0342',
                n='82962.8',
                e='81301',
                s='-156060.2',
                w='-146082.6',
                )

    def _calculate_basins(self):
        logger.info('Calculating watershed basins.')
        self.grass.run_command('r.watershed',
                elevation=input_layer,
                threshold=10000,     # cell units
                drainage=output_drainage,
                basin=tmp_basin,
                stream=tmp_stream,
                flags='b'           # Multi-stream, 8 directions, beautify flat areas
                )

    def _vectorize_basins(self):
        self.grass.run_command('r.to.vect',
                input=tmp_basin,
                out=output_basin,
                flags='v',     # Remember raster value as vector category (so colors line up)
                type='area')



    def _thin_streams(self):
        logger.info('Thinning raster streams.')
        self.grass.run_command('r.thin',
                input=tmp_stream,
                output=tmp_stream_thinned)

    def _vectorize_streams(self):
        logger.info('Vectorizing stream segments.')
        self.grass.run_command('r.to.vect',
                input=tmp_stream_thinned,
                output=output_stream,
                type='line')

    def _clean_temp_files(self):
        logger.info('Cleaning watershed temp files.')
        self.grass.run_command('g.remove', type='raster', name=tmp_stream, flags='f')
        self.grass.run_command('g.remove', type='raster', name=tmp_stream_thinned, flags='f')
        self.grass.run_command('g.remove', type='raster', name=tmp_basin, flags='f')
        self.grass.run_command('g.remove', type='raster', name=tmp_clipped_elevation, flags='f')
