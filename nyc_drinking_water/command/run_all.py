from logzero import logger

from . import Base
from .. import command

class RunAll(Base):
    def _run(self):
        logger.info('Running all steps.')

        all_commands = [
            command.ingest_dem.IngestDEM,
            command.hillshade.Hillshade,
            command.basins.Basins,
            command.reservoirs.Reservoirs,
            command.watersheds.Watersheds
        ]

        for cmd in all_commands:
            cmd(self.opts).run()
