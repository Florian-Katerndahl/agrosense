import json
import sys
from shapely.geometry import Polygon
import geopandas as gpd
import argparse
import pandas as pd

def read_json(file_path: str) -> dict:
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def transform_coordinates(circle_coordinates: list, origin: tuple, pixel_size: tuple) -> list:
    transformed_circles = []
    x_origin, y_origin = origin
    x_size, y_size = pixel_size
    
    for circle in circle_coordinates:
        transformed_circle = []
        for x, y in circle:
            spatial_x = x_origin + x * x_size
            spatial_y = y_origin - y * y_size
            transformed_circle.append((spatial_x, spatial_y))
        transformed_circles.append(transformed_circle)
    return transformed_circles

def create_geodataframe(transformed_circles: list, crs: str) -> gpd.GeoDataFrame:
    polygons = [Polygon(circle) for circle in transformed_circles]
    gdf = gpd.GeoDataFrame(geometry=polygons, crs=crs)
    return gdf

def save_geodataframe(gdf: gpd.GeoDataFrame, output_file: str) -> None:
    gdf.to_file(output_file)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transform image coordinates to spatial coordinates and save as a spatial vector dataset."
    )
    parser.add_argument(
        '--input-file',
        type=str,
        required=True,
        help='Path to the input JSON file.'
    )
    parser.add_argument(
        '--output-file',
        type=str,
        required=True,
        help='Path to the output file.'
    )
    parser.add_argument(
        '--origins',
        type=float,
        nargs='+',
        required=True,
        help='List of raster origins (x_origin y_origin for each image).'
    )
    parser.add_argument(
        '--pixel-sizes',
        type=float,
        nargs='+',
        required=True,
        help='List of pixel sizes (x_size y_size for each image).'
    )
    parser.add_argument(
        '--crs',
        type=str,
        nargs='+',
        required=True,
        help='List of Coordinate Reference Systems (CRS) for each image.'
    )

    args = parser.parse_args()

    # Validate the number of origins, pixel sizes, and CRS
    if len(args.origins) % 2 != 0 or len(args.pixel_sizes) % 2 != 0 or len(args.crs) == 0:
        print("Error: Origins and pixel sizes should be provided in pairs (x, y), and CRS should be provided for each image.")
        sys.exit(1)

    num_images = len(args.origins) // 2
    origins = [(args.origins[i * 2], args.origins[i * 2 + 1]) for i in range(num_images)]
    pixel_sizes = [(args.pixel_sizes[i * 2], args.pixel_sizes[i * 2 + 1]) for i in range(num_images)]
    crs_list = args.crs
    
    if len(crs_list) != num_images:
        print("Error: The number of CRS provided should match the number of images.")
        sys.exit(1)
    
    # Step 1: Read the JSON file
    data = read_json(args.input_file)
    
    coordinates = {}
    for key, circle_coordinates in data.items():
        if key not in data:
            continue
        
        # Determine the index of the image based on the key
        image_index = list(data.keys()).index(key)
        
        # Step 2: Transform coordinates
        transformed_circles = transform_coordinates(circle_coordinates, origins[image_index], pixel_sizes[image_index])
        
        coordinates[key] = transformed_circles  

    # Step 3: Create a GeoDataFrame for each image and merge them
    all_gdfs = []
    for image_index, (key, transformed_circles) in enumerate(coordinates.items()):
        gdf = create_geodataframe(transformed_circles, crs_list[image_index])
        all_gdfs.append(gdf)
    
    # Merge all GeoDataFrames into one
    merged_gdf = gpd.GeoDataFrame(pd.concat(all_gdfs, ignore_index=True))
    
    # Step 4: Save the output
    save_geodataframe(merged_gdf, args.output_file)
    print(f"GeoDataFrame saved to {args.output_file}")

    return 0
