import json
import sys
from shapely.geometry import Point, Polygon
import geopandas as gpd
import argparse

def read_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def transform_coordinates(circle_coordinates, origin, pixel_size):
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

def create_geodataframe(transformed_circles, crs):
    polygons = [Polygon(circle) for circle in transformed_circles]
    gdf = gpd.GeoDataFrame(geometry=polygons, crs=crs)
    return gdf

def save_geodataframe(gdf, output_file):
    gdf.to_file(output_file)

def main():

    parser = argparse.ArgumentParser(description="Transform image coordinates to spatial coordinates and save as a spatial vector dataset.")
    parser.add_argument('--input-file, type=str, required=True, help='Path to the input JSON file.')
    parser.add_argument('--output-file', type=str, required=True, help='Path to the output file.')
    parser.add_argument('--origin', type=float, nargs=2, required=True, help='Raster origin (x_origin y_origin).')
    parser.add_argument('--pixel-size', type=float, nargs=2, required=True, help='Pixel size (x_size y_size).')
    parser.add_argument('--crs', type=str, required=True, help='Coordinate Reference System (CRS).')

    args = parser.parse_args()
    
    # Step 1: Read the JSON file
    data = read_json(args.input_file)
    
    # Assuming data contains only one key for simplicity
    key = list(data.keys())[0]
    circle_coordinates = data[key]
    
    # Step 2: Transform coordinates
    transformed_circles = transform_coordinates(circle_coordinates, tuple(args.origin), tuple(args.pixel_size))
    
    # Step 3: Create a GeoDataFrame
    gdf = create_geodataframe(transformed_circles, args.crs)
    
    # Step 4: Save the output
    save_geodataframe(gdf, args.output_file)
    print(f"GeoDataFrame saved to {args.output_file}")
