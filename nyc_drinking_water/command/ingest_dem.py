import os
import re
import subprocess
from logzero import logger

import nyc_drinking_water as ndw
from . import Base

dem_regex = r'ASTGTM2_(N\d+W\d+)_dem.tif'
dem_glob = 'N*W*'
aster_dir = os.path.join(ndw.data_dir, 'ASTER')

output_layer = 'concatenated_dems'

class IngestDEM(Base):
    def __init__(self, opts):
        super(IngestDEM, self).__init__(opts)

        self.input_files = [os.path.join(aster_dir, f)
                for f in os.listdir(aster_dir)
                if re.match(dem_regex, f)]

    def _run(self):
        self._reproject_dems()
        self._reset_viewport()
        self._concatenate_dems()
        self._copy_to_postgres()
        self._clean_input_dems()

    def _reproject_dems(self):
        logger.info('Importing DEMs.')
        logger.debug(self.input_files)
        for input_dem in self.input_files:
            self.grass.run_command(
                    'r.import',
                    input=input_dem,
                    output=self._renamed_dem(input_dem))

    def _reset_viewport(self):
        logger.info('Resetting viewport to include all DEMs.')
        self.grass.run_command('g.region',
                flags='p',
                raster=','.join(self._imported_files()))

    def _concatenate_dems(self):
        logger.info('Concatenating all DEMs.')
        self.grass.run_command('r.patch',
                input=','.join(self._imported_files()),
                output=output_layer)

    def _copy_to_postgres(self):
        logger.info('Copying rasters to PostGIS.')
        self.grass.run_command('r.out.gdal',
                input=output_layer,
                output='tmp/concatenated_dems.tif',
                format='GTiff')

        sql_file = open('tmp/concatenated_dems.sql', 'w+')
        subprocess.call([
                'raster2pgsql',
                '-s', '200100',
                '-I',
                '-M',
                '-l', '2,4,8,16,32,64,128,256,512,999',
                '-t', '100x100',
                'tmp/concatenated_dems.tif',
                'dem.dem'
            ],
            stdout=sql_file
        )
        sql_file.seek(0)
        subprocess.call(['psql', 'ndw', '-c', 'drop schema dem cascade'])
        subprocess.call(['psql', 'ndw', '-c', 'create schema dem'])
        subprocess.call(['psql', 'ndw'], stdin=sql_file)

    def _clean_input_dems(self):
        logger.info('Cleaning source DEMs.')
        self.grass.run_command('g.remove', type='raster', pattern=dem_glob, flags='f')
        os.remove('tmp/concatenated_dems.tif')

    @staticmethod
    def _renamed_dem(original_path):
        return re.sub(dem_regex, '\\1', os.path.basename(original_path))

    def _imported_files(self):
        return [i[0] for i in self.grass.list_pairs('raster', pattern=dem_glob)]
