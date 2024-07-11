"""
spatialtransformer.py

This module provides functionality to read JSON files with circle coordinates,
transform these coordinates, create a GeoDataFrame, and save it as a file.
"""

import json
from typing import List, Tuple, Dict
from shapely.geometry import Polygon
import geopandas as gpd


class SpatialTransformer:
    """
    A class to handle spatial transformations of coordinates and conversion
    into GeoDataFrames.
    """

    def __init__(self):
        """
        Initializes the SpatialTransformer class.
        """
        pass

    def read_json(
        self,
        file_path: str
    ) -> Dict[str, List[List[Tuple[float, float]]]]:
        """
        Reads a JSON file containing circle coordinates.

        Args:
            file_path (str): The path to the JSON file.

        Returns:
            Dict[str, List[List[Tuple[float, float]]]]: The data
            loaded from the JSON file.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data

    def transform_coordinates(
        self,
        circle_coordinates: List[List[Tuple[float, float]]],
        origin: Tuple[float, float],
        pixel_size: Tuple[float, float]
    ) -> List[List[Tuple[float, float]]]:
        """
        Transforms circle coordinates based on the origin and pixel size.

        Args:
            circle_coordinates (List[List[Tuple[float, float]]]): List of
            circles with coordinates.
            origin (Tuple[float, float]): The origin point for transformation.
            pixel_size (Tuple[float, float]): pixel size for transformation.

        Returns:
            List[List[Tuple[float, float]]]: Transformed coordinates.
        """
        transformed_circles = []
        x_origin, y_origin = origin
        x_size, y_size = pixel_size

        for circle in circle_coordinates:
            transformed_circle = []
            for x, y in circle:
                spatial_x = x_origin + x * x_size
                spatial_y = y_origin + y * y_size
                transformed_circle.append((spatial_x, spatial_y))
            transformed_circles.append(transformed_circle)
        return transformed_circles

    def create_geodataframe(
        self,
        transformed_circles: List[List[Tuple[float, float]]],
        crs: str
    ) -> gpd.GeoDataFrame:
        """
        Creates a GeoDataFrame from the transformed circle coordinates.

        Args:
            transformed_circles (List[List[Tuple[float, float]]]):
                Transformed circle coordinates.
            crs (str): The coordinate reference system.

        Returns:
            gpd.GeoDataFrame: The resulting GeoDataFrame.
        """
        polygons = [Polygon(circle) for circle in transformed_circles]
        gdf = gpd.GeoDataFrame(geometry=polygons, crs=crs)
        return gdf

    def save_geodataframe(
        self,
        gdf: gpd.GeoDataFrame, output_file: str
    ) -> None:
        """
        Saves the GeoDataFrame to a file.

        Args:
            gdf (gpd.GeoDataFrame): The GeoDataFrame to save.
            output_file (str): The path to the output file.
        """
        gdf.to_file(output_file, driver='GPKG')
