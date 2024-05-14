from malstroem.scripts import complete
import geopandas as gpd
from django.contrib.gis.db.models import Union
from skb.utils import to_gdf, flatten_3d_multilinestring
from skb.service.geo import RasterService

from skb.models import (
    Stikkrenne, 
    Byggflate,
    MalstroemRun,
)

raster_service = RasterService(prefix='nhm')

malstroem_run = MalstroemRun.objects.get(name='test-4563')

union_geom = malstroem_run.catchments.aggregate(union=Union('geometry'))['union']

byggflater = Byggflate.objects.filter(geometry__intersects=union_geom)

stikkrenner = Stikkrenne.objects.filter(geometry__intersects=union_geom)
gdf_stikkrenner = to_gdf(stikkrenner, crs='EPSG:25833')

gdf_stikkrenner['minz'] = gdf_stikkrenner['geometry'].apply(lambda x: min(flatten_3d_multilinestring(x)[1]))

catchment = malstroem_run.catchments.first()
file_path = raster_service.storage_service.fetch_and_cache_file(catchment.dtm.key)

result = complete._process_all(
    file_path,
    './outdir/',
    None,
    "volume > 2.5",
    20,
    0.1,
    None,
    gdf_stikkrenner=gdf_stikkrenner,
    gdf_byggflater=None,
    noise_level=0
)

# _process_all(dem, outdir, accum, filter, mm, zresolution, vector, gdf_stikkrenner=None, gdf_byggflater=None, noise_level=0):