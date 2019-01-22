import re
from collections import namedtuple
from logzero import logger
from .. import projection

from . import Base

class Reservoirs(Base):
    table_name = 'reservoirs'

    create_sql = """
        CREATE TABLE %s (
          id bigserial PRIMARY KEY,
          name varchar NOT NULL,
          system varchar NOT NULL,
          geom geometry(MultiPolygon, %s) NOT NULL
        );
    """ % (table_name, projection.srid)

    index_sql = [
            "CREATE INDEX %s_geom ON %s USING GIST (geom)",
            "CREATE INDEX %s_system ON %s (system)",
            ]

    insert_sql = """
        INSERT INTO %s
        (name, system, geom)
        SELECT %%s, %%s, ST_Multi(ST_Union(w.geom))
        FROM water w
        WHERE w.name IN %%s
          AND w.state_postal_code = 'NY'
    """ % (table_name)

    def _run(self):
        logger.info('Calculating reservoir boundaries and low points.')

        self._ingest_reservoirs()

    def _drop_table(self):
        self.db.cursor().execute("DROP TABLE IF EXISTS %s" % self.table_name)

    def _ingest_reservoirs(self):
        logger.info('Defining reservoir boundaries.')
        for reservoir in reservoirs:
            self.db.cursor().execute(self.insert_sql, (
                reservoir.output_name,
                reservoir.system,
                reservoir.input_name
                ))


class ReservoirStruct(object):
    def __init__(self, input_name, output_name, system):
        self.input_name = input_name
        self.output_name = output_name
        self.system = system
        self.sanitized_name = re.sub('[^a-zA-Z]', '_', self.output_name)


reservoirs = [
    ReservoirStruct(('Cannonsville Reservoir',), 'Cannonsville Reservoir', 'Delaware'),
    ReservoirStruct(('Neversink Reservoir',), 'Neversink Reservoir', 'Delaware'),
    ReservoirStruct(('Pepacton Reservoir',), 'Pepacton Reservoir', 'Delaware'),
    ReservoirStruct(('Rondout Reservoir',), 'Rondout Reservoir', 'Delaware'),

    ReservoirStruct(('Ashokan Reservoir',), 'Ashokan Reservoir', 'Catskill'),
    ReservoirStruct(('Schoharie Reservoir',), 'Schoharie Reservoir', 'Catskill'),

    ReservoirStruct(('Amawalk Reservoir',), 'Amawalk Reservoir', 'Croton'),
    ReservoirStruct(('Bog Brook Reservoir',), 'Bog Brook Reservoir', 'Croton'),
    ReservoirStruct(('Boyd Corners Reservoir',), 'Boyd\'s Corners Reservoir', 'Croton'),
    ReservoirStruct(('Cross River Reservoir',), 'Cross River Reservoir', 'Croton'),
    ReservoirStruct(('Croton Falls Reservoir',), 'Croton Falls Reservoir', 'Croton'),
    ReservoirStruct(('Croton Lk',), 'Croton Lake', 'Croton'),
    ReservoirStruct(('Diverting Reservoir',), 'Diverting Reservoir', 'Croton'),
    ReservoirStruct(('East Branch Reservoir',), 'East Branch Reservoir', 'Croton'),
    ReservoirStruct(('Hillview Resv',), 'Hillview Reservoir', 'Croton'),
    ReservoirStruct(('Kensico Reservoir',), 'Kensico Reservoir', 'Croton'),
    ReservoirStruct(('Jerome Park Reservoir',), 'Jerome Park Reservoir', 'Croton'),
    ReservoirStruct(('Kirk Lk',), 'Kirk Lake', 'Croton'),
    ReservoirStruct(('Lk Gilead',), 'Lake Gilead', 'Croton'),
    ReservoirStruct(('Lk Gleneida',), 'Lake Gleneida', 'Croton'),
    ReservoirStruct(('Middle Branch Reservoir',), 'Middle Branch Reservoir', 'Croton'),
    ReservoirStruct(('Muscoot Reservoir','Muskoot Reservoir',), 'Muscoot Reservoir', 'Croton'),
    ReservoirStruct(('New Croton Reservoir',), 'New Croton Reservoir', 'Croton'),
    ReservoirStruct(('Titicus Reservoir',), 'Titicus Reservoir', 'Croton'),
    ReservoirStruct(('West Branch Reservoir',), 'West Branch Reservoir', 'Croton'),
]

