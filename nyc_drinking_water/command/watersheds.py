from logzero import logger

from . import Base
from .basins import output_drainage as input_drainage

class Watersheds(Base):
    def _run(self):
        logger.error('As yet unimplemented.')
        # Loop through all reservoirs in database
            # Find lowest point in DEM for the reservoir
            # Calculate r.water.outlet with that point
            # Vectorize output raster
            # Clean up raster
        pass

        # self.grass.run_command('r.water.outlet',
        #         input=input_drainage,
        #         output=some_output_file,
        #         coordinates='513063.086,1082204.467')
