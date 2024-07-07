import json
from shapely.geometry import Polygon
import geopandas as gpd
from typing import List, Tuple, Dict

class SpatialTransformer:
    def __init__(self):
        pass

    def read_json(self, file_path: str) -> Dict[str, List[List[Tuple[float, float]]]]:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data

    def transform_coordinates(
        self, 
        circle_coordinates: List[List[Tuple[float, float]]], 
        origin: Tuple[float, float], 
        pixel_size: Tuple[float, float]
    ) -> List[List[Tuple[float, float]]]:
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
        polygons = [Polygon(circle) for circle in transformed_circles]
        gdf = gpd.GeoDataFrame(geometry=polygons, crs=crs)
        return gdf

    def save_geodataframe(self, gdf: gpd.GeoDataFrame, output_file: str) -> None:
        gdf.to_file(output_file, driver='GPKG')

