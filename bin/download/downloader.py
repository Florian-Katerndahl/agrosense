import os

from datetime import datetime
from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer
from typing import List, Tuple


def get_credentials(args):
    # retrieve username and password from arguments
    username = args.username
    password = args.password
    # if arguments not provided retrieve from environment variables
    if username is None:
        username = os.environ.get('USGS_USERNAME')
    if password is None:
        password = os.environ.get('USGS_PASSWORD')
    # if not saved as environment variable return error message and exit
    if username is None or password is None:
        raise ValueError("Error: Username and Password must be set either as"
                         " arguments or as environment variables"
                         " (USGS_USERNAME, USGS_PASSWORD).")

    return username, password


def get_bounding_box(coordinates: List[Tuple[float, float]]) -> List[float]:
    # collect latitudes and longitudes separately from input
    latitudes = [coordinate[0] for coordinate in coordinates]
    longitudes = [coordinate[1] for coordinate in coordinates]
    # create bounding box through calculating maximums and minimums
    bounding_box = [min(longitudes), min(latitudes),
                    max(longitudes), max(latitudes)]

    return bounding_box


def search_and_download_data(username: str, password: str,
                             coordinates: List[Tuple[float, float]],
                             start_date: str, end_date: str, output_dir: str,
                             max_cloud_cover: int = 10,
                             max_results: int = 100,
                             download: bool = True) -> None:
    # Input Validation
    # check range of max_cloud_cover and max_results after converting into int
    if max_results is not None:
        max_results = int(max_results)
        if not 0 <= max_results <= 50000:
            raise ValueError("Error: max_results should be set"
                             " between 0-50.000.")
    if max_cloud_cover is not None:
        max_cloud_cover = int(max_cloud_cover)
        if not 0 <= max_cloud_cover <= 100:
            raise ValueError("Error: max_cloud_cover should"
                             " be between 0-100%.")
    # check whether coordinate input is valid
    for coordinate in coordinates:
        if not isinstance(coordinate, tuple) or len(coordinate) != 2:
            raise ValueError("Error: Each coordinate must be a tuple of two"
                             " elements. Either a coordinate tuple is empty or"
                             " one latitude/longitude variable is missing.")
        latitude, longitude = coordinate
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            raise ValueError("Error: Invalid latitude or longitude value.")
    # check whether start_date is before end_date
    if (datetime.strptime(start_date, "%Y-%m-%d")
            >= datetime.strptime(end_date, "%Y-%m-%d")):
        raise ValueError("Error: The start_date must be before the end_date.")
    # Search and Download
    # login to API and EarthExplorer
    api = API(username, password)
    earth_explorer = EarthExplorer(username, password)
    # search depending on the number of coordinates
    if len(coordinates) == 1:
        # search for scenes if coordinates only contains one searching point
        scenes = api.search(dataset="landsat_ot_c2_l2", start_date=start_date,
                            end_date=end_date,
                            max_cloud_cover=max_cloud_cover,
                            max_results=max_results,
                            latitude=coordinates[0][0],
                            longitude=coordinates[0][1])
    elif len(coordinates) >= 2:
        # get bounding box from coordinates
        bounding_box = get_bounding_box(coordinates)
        # search for scenes through a bounding box
        scenes = api.search(dataset="landsat_ot_c2_l2", start_date=start_date,
                            end_date=end_date,
                            max_cloud_cover=max_cloud_cover,
                            max_results=max_results, bbox=bounding_box)
    else:
        raise ValueError("Error: Expected at least one coordinate pair,"
                         " but got none.")
    # give the user fieedback on how many scenes were found
    print(f"Found {len(scenes)} scenes.")
    # download each found scene if the user chose to download
    if download:
        for scene in scenes:
            earth_explorer.download(scene["landsat_product_id"],
                                    output_dir=output_dir)
    # logout of API and EarthExplorer
    api.logout()
    earth_explorer.logout()
