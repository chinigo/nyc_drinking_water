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

        klassmap = {
            'ingest_dem': ingest_dem.IngestDEM,
            'hillshade': hillshade.Hillshade,
            'basins': basins.Basins,
            'reservoirs': reservoirs.Reservoirs,
            'watersheds': watersheds.Watersheds
        }

        subparsers = parser.add_subparsers(title='commands')
        for kommand, klass in klassmap.iteritems():
            subcommand = subparsers.add_parser(kommand)
            subcommand.set_defaults(klass=klass)

        return parser

    def __parsed_args(self):
        return self.parser.parse_args(args=self.argv)
