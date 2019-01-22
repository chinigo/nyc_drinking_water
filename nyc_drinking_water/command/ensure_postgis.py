from logzero import logger
from . import Base
from .. import projection

class EnsurePostGIS(Base):
    def _run(self):
        self.db.cursor().execute('CREATE EXTENSION IF NOT EXISTS postgis')
        self.db.cursor().execute("""
            INSERT INTO spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text)
            VALUES (%i,'%s', %i, '%s', '%s')
            ON CONFLICT (srid) DO NOTHING
        """ % (projection.srid, projection.authority, projection.srid, projection.wkt, projection.proj4))
