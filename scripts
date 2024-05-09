import geopandas as gpd
import pandas as pd
import os
from .dtm_perturbations_create import repair_linestring_gpkg
import numpy as np
from scipy.signal import convolve2d
import rasterio
from rasterio.features import rasterize


def repair_geometries(base_dir):
    """
    Repair geometries in the shapefiles in the directories specified in the list dirs.
    """

    for subdir, dirs, files in os.walk(base_dir):
        for file in files:
            if file=='malstroem.gpkg':
                input_file = os.path.join(subdir, file)
                streams_output_file=f"{base_dir}/{os.path.basename(subdir)}.gpkg".replace('merged', 'streams')
                print(f"Repairing {input_file} to {streams_output_file}")
                repair_linestring_gpkg(input_file, 'streams', streams_output_file)

def extract_bluespots(base_dir):
    for subdir, dirs, files in os.walk(base_dir):
        for file in files:
            if file=='malstroem.gpkg':
                input_file = os.path.join(subdir, file)
                bluespots_output_file=f"{base_dir}/{os.path.basename(subdir)}.gpkg".replace('merged', 'bluespots')
                print(f"Copying bluespots from {input_file} to {bluespots_output_file}")
                gdf = gpd.read_file(input_file, layer='finalbluespots')
                gdf.to_file(bluespots_output_file, driver='GPKG')
def crop_geometries(gdf, polygon):

    polygon_gdf = gpd.GeoDataFrame(geometry=[polygon], crs=gdf.crs)
    cropped_gdf = gpd.overlay(gdf, polygon_gdf, how='intersection')

    cropped_gdf = cropped_gdf[~cropped_gdf.is_empty]
    return cropped_gdf


def combine_results(gdf, results_dir):
    """
    Combine the results of the model runs in the directories specified in the list dirs.
    """

    if not os.path.exists(results_dir):
        print(f"Directory {results_dir} does not exist.")
        return None
    
    gdf_streams = gpd.GeoDataFrame()
    gdf_bluespots = gpd.GeoDataFrame()

    crs = gdf.crs

    for index, row in gdf.iterrows():
        streams_file = f"{results_dir}/streams_{row['vassdragsnummer']}.gpkg"
        bluespots_file = f"{results_dir}/bluespots_{row['vassdragsnummer']}.gpkg"  

        polygon = row['geometry']
        print("Processing: ", row["vassdragsnummer"])

        gdf_streams_dir = gpd.read_file(streams_file).to_crs(crs)
        gdf_bluespots_dir = gpd.read_file(bluespots_file).to_crs(crs)

        gdf_streams_dir = gdf_streams_dir.clip(polygon)
        gdf_bluespots_dir = gdf_bluespots_dir.clip(polygon)

        gdf_streams_dir['vassdragsnummer'] = row['vassdragsnummer']
        gdf_bluespots_dir['vassdragsnummer'] = row['vassdragsnummer']

        gdf_streams = gpd.GeoDataFrame(pd.concat([gdf_streams, gdf_streams_dir], ignore_index=True), crs=crs)
        gdf_bluespots = gpd.GeoDataFrame(pd.concat([gdf_bluespots, gdf_bluespots_dir], ignore_index=True), crs=crs)
    
    return gdf_streams, gdf_bluespots

def combine_streams(filenames):
    gdf = gpd.GeoDataFrame()
    n=0
    for file in filenames:
        print(file)
        part = gpd.read_file(file)
        n+=part.shape[0]
        gdf = gpd.GeoDataFrame(pd.concat([gdf, part], ignore_index=True), crs=part.crs)
    return gdf, n

def burn_line(geom, value):
    return ((g, value) for g in geom)

def gdf_to_raster(gdf):
    # Example: Define raster resolution and bounds
    cell_size = 1.0  # size of the cell in the units of the coordinate system (e.g., meters)
    bounds = gdf.total_bounds  # minx, miny, maxx, maxy
    width = int((bounds[2] - bounds[0]) / cell_size)
    height = int((bounds[3] - bounds[1]) / cell_size)
    raster = np.zeros((height, width), dtype=np.uint8)

    # Define transformation from pixel coordinates to geographic coordinates
    transform = rasterio.transform.from_bounds(*bounds, width, height)

    rasterized_lines = rasterize(burn_line(gdf.geometry, 1), out_shape=(height, width), transform=transform, fill=0, dtype=np.uint8)

    # # Optionally, merge this with the existing raster
    # raster |= rasterized_lines  # This assumes raster is already initialized as shown above

    exposure = compute_exposure(rasterized_lines)
    return rasterized_lines, transform, exposure

def compute_exposure(binary_raster, n=6):

    kernel = np.ones((n,n))  
    intersection_count = convolve2d(binary_raster, kernel, mode='same', boundary='wrap')
    return intersection_count

def save_raster(file_path, raster, transform, crs):
    # Save the raster to a new file
    with rasterio.open(
        file_path, 'w',
        driver='GTiff',
        height=raster.shape[0],
        width=raster.shape[1],
        count=1,
        dtype=raster.dtype,
        crs=crs,
        transform=transform,
    ) as dst:
        dst.write(raster, 1)

