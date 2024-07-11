"""
Script to transform image coordinates to spatial coordinates
and save them as a spatial vector dataset.
"""

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace
import sys
from typing import List, Tuple, Dict
import pandas as pd
import geopandas as gpd
from senseagronomy import SpatialTransformer

def main() -> None:
    """
    Main function to parse arguments and transform coordinates.
    """
    parser: ArgumentParser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description=(
            "Transform image coordinates to spatial coordinates "
            "and save as a spatial vector dataset."
        )
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
        required=True,
        help='Coordinate Reference System (CRS).'
    )

    args: Namespace = parser.parse_args()

    # Validate the number of origins and pixel sizes
    if len(args.origins) % 2 != 0 or len(args.pixel_sizes) % 2 != 0:
        sys.stderr.write("Error: Origins and pixel sizes should be provided in pairs (x, y).\n")
        sys.exit(1)

    num_images: int = len(args.origins) // 2
    origins: List[Tuple[float, float]] = [
        (args.origins[i * 2], args.origins[i * 2 + 1]) for i in range(num_images)
    ]
    pixel_sizes: List[Tuple[float, float]] = [
        (args.pixel_sizes[i * 2], args.pixel_sizes[i * 2 + 1]) for i in range(num_images)
    ]
    crs: str = args.crs

    transformer: SpatialTransformer = SpatialTransformer()

    # Step 1: Read the JSON file
    data: Dict[str, List[List[Tuple[float, float]]]] = transformer.read_json(args.input_file)

    coordinates: Dict[str, List[List[Tuple[float, float]]]] = {}
    data_keys = list(data.keys())
    for key, circle_coordinates in data.items():
        if key not in data:
            continue

        # Determine the index of the image based on the key
        image_index: int = data_keys.index(key)

        # Step 2: Transform coordinates
        transformed_circles: List[List[Tuple[float, float]]] = transformer.transform_coordinates(
            circle_coordinates, origins[image_index], pixel_sizes[image_index]
        )

        coordinates[key] = transformed_circles

    # Step 3: Create a GeoDataFrame for each image and merge them
    all_gdfs: List[gpd.GeoDataFrame] = []
    for transformed_circles in coordinates.values():
        gdf: gpd.GeoDataFrame = transformer.create_geodataframe(transformed_circles, crs)
        all_gdfs.append(gdf)

    # Merge all GeoDataFrames into one
    merged_gdf: gpd.GeoDataFrame = gpd.GeoDataFrame(pd.concat(all_gdfs, ignore_index=True))

    # Step 4: Save the output to SQLite using GeoPackage format
    transformer.save_geodataframe(merged_gdf, args.output_file)
    print(f"GeoDataFrame saved to {args.output_file}")

    return 0
