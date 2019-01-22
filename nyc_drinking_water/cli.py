import argparse

from .command import *

class Cli:
    def __init__(self, argv):
        self.argv = argv[1:]
        self.parser = self.__create_parser()

    def run(self):
        opts = self.parser.parse_args(args=self.argv)
        opts.klass(opts).run()

    def __create_parser(self):
        parser = argparse.ArgumentParser(prog='nyc_drinking_water')
        parser.add_argument(
                '-f',
                '--force',
                default=False,
                action='store_true',
                help='Overwrite existing data if it exists?')
        parser.add_argument(
                '-v',
                '--verbose',
                default=False,
                action='store_true')

        parser.add_argument(
                '-c',
                '--connection',
                default='postgres://localhost/ndw',
                help='Connection string to PostGIS database containing TIGER data.'
                )

        klassmap = {
            'all':            [run_all.RunAll, 'Run all steps in dependency order.'],
            'ensure_postgis': [ensure_postgis.EnsurePostGIS, 'Install PostGIS and custom projection.'],
            'ingest_dem':     [ingest_dem.IngestDEM, 'Ingest and concatenate input DEMs.'],
            'hillshade':      [hillshade.Hillshade, 'Calculate pretty 3D hillshade from concatenated DEM.'],
            'basins':         [basins.Basins, 'Calculate drainage basins and stream network from concatenated DEM.'],
            'reservoirs':     [reservoirs.Reservoirs, 'Ingest reservoir definitions, given TIGER dataset.'],
            'watersheds':     [watersheds.Watersheds, 'Calculate watersheds for each reservoir from drainage basins.'],
            'pipelines':      [pipelines.Pipelines, 'Georeference pipelines.']
        }

        subparsers = parser.add_subparsers(title='commands')
        for (kommand, (klass, help)) in klassmap.iteritems():
            subcommand = subparsers.add_parser(kommand, help=help)
            subcommand.set_defaults(klass=klass)

        return parser

    def __parsed_args(self):
        return self.parser.parse_args(args=self.argv)
