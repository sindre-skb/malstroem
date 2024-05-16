from malstroem.scripts import complete
import geopandas as gpd
from django.contrib.gis.db.models import Union
from skb.utils import to_gdf, flatten_3d_multilinestring
from skb.service.geo import RasterService
from shapely import wkt
from django.contrib.gis.geos import GEOSGeometry

from skb.models import (
    Pipe, 
    Byggflate,
    MalstroemRun,
)

raster_service = RasterService(prefix='nhm')

malstroem_run = MalstroemRun.objects.get(name='test-1568')

union_geom = malstroem_run.catchments.aggregate(union=Union('geometry'))['union']
gdf_union = gpd.GeoDataFrame(geometry=[wkt.loads(union_geom.wkt)], crs='EPSG:25833').to_crs('EPSG:4326')
union_geom_4326 = GEOSGeometry(gdf_union.loc[0, 'geometry'].wkt)

byggflater = Byggflate.objects.filter(geometry__intersects=union_geom_4326)
stikkrenner = Pipe.objects.filter(geometry__intersects=union_geom)

gdf_stikkrenner = to_gdf(stikkrenner, crs='EPSG:25833')
gdf_byggflater = to_gdf(byggflater, crs='EPSG:4326').to_crs('EPSG:25833')

gdf_stikkrenner['offset'] = gdf_stikkrenner['geometry'].apply(lambda x: min(flatten_3d_multilinestring(x)[1]))

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
    gdf_byggflater=gdf_byggflater,
    noise_level=0
)
