from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer
from typing import List, Tuple


def get_bounding_box(coordinates: List[Tuple[float, float]]) -> List[float]:
    latitudes = [coordinate[0] for coordinate in coordinates]
    longitudes = [coordinate[1] for coordinate in coordinates]  
    return [min(longitudes), min(latitudes), max(longitudes), max(latitudes)]


def search_and_download_data(username: str, password: str, coordinates: List[Tuple[float, float]], start_date: str, end_date: str, 
                             max_cloud_cover: int, max_results: int, output_dir: str) -> None: 
    # login to API and EarthExplorer
    api = API(username, password)
    earth_explorer = EarthExplorer(username, password)
    # get bounding box from coordinates
    bounding_box = get_bounding_box(coordinates)
    # search for scenes
    scenes = api.search(
        dataset="landsat_ot_c2_l2",
        start_date=start_date, 
        end_date=end_date, 
        max_cloud_cover=max_cloud_cover,
        max_results=max_results,
        bbox=bounding_box)
    # download each found scene
    for scene in scenes: 
        earth_explorer.download(scene["landsat_product_id"], output_dir=output_dir)
    # logout of API and EarthExplorer
    api.logout()
    earth_explorer.logout()
