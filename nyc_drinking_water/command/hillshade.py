import contextlib
import os
import subprocess
from logzero import logger

from . import Base
from .ingest_dem import output_layer as input_layer

output_layer = 'relief'
tiff_filename = 'tmp/hillshade.tif'
sql_filename = 'tmp/hillshade.sql'

class Hillshade(Base):
    def _run(self):
        self._calculate_relief()
        self._copy_to_postgres()
        self._clean_temp_files()

    def _calculate_relief(self):
        logger.info('Calculating shaded relief map.')
        self.grass.run_command('r.relief',
                input=input_layer,
                output=output_layer,
                zscale='2')

    def _copy_to_postgres(self):
        logger.info('Copying hillshade to postgres')
        self.grass.run_command('r.out.gdal',
                input=output_layer,
                output=tiff_filename,
                format='GTiff')

        sql_file = open(sql_filename, 'w+')
        subprocess.call([
                'raster2pgsql',
                '-s', '200100',
                '-I',
                '-M',
                '-l', '2,4,8,16,32,64,128,256,512,999',
                '-t', '100x100',
                tiff_filename,
                'hillshade.hillshade'
            ],
            stdout=sql_file
        )
        sql_file.seek(0)
        subprocess.call(['psql', 'ndw', '-c', 'DROP SCHEMA IF EXISTS hillshade CASCADE'])
        subprocess.call(['psql', 'ndw', '-c', 'CREATE SCHEMA hillshade'])
        subprocess.call(['psql', 'ndw'], stdin=sql_file)

    def _clean_temp_files(self):
        self.grass.run_command('g.remove', type='rast', name=output_layer, flags='f')
        for path in [tiff_filename, sql_filename]:
            if os.path.exists(path):
                logger.debug('Removing %s' % path)
                os.remove(path)
