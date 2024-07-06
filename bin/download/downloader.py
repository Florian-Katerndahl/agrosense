#!/usr/bin/env python3

"""
This script contains three functions: 'get_credentials', 'get_bounding_box',
and 'search_and_download_data'.

'get_credentials' is responsble for obtainting the username and password
either from the arguments passed or from the environment variables.

'get_bounding_box' calculates the bounding box for a given list of
coordinates.

'search_and_download_data' logs into the USGS API and EarthExplorer with the
provided credentials, performs a search based on the specified parameters,
and optionally downloads the found scenes.
"""

import os

from datetime import datetime
from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer
from typing import List, Tuple


def get_credentials(args):
    """
    This function retrieves the username and password from the provided
    arguments. If the username or password is not provided, it attempts
    to retrieve them from the environment variables.

    Parameters:
        args (object): An object that contains the username and password
                       as attributes.

    Returns:
        tuple (tuple): A tuple contraining username and password as strings.

    Raises:
        ValueError: If the username or password is not provided either as an
                    argument or as an environment variable.
    
    Note:
        If username and password are saved in environment variables the names
        'USGS_USERNAME' and 'USGS_PASSWORD' should be used.
    """
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
    """
    This function calculates the bounding box for a given list of coordinates.

    Parameters:
        coordinates (List[Tuple[float, float]]): A list of tuples where each
        tuple represents a pair of latitude and longitude for one coordinate.

    Returns:
        bounding_box (List[float]): A list of four float values representing
        the bounding box. The order ist minimal longitude, minimal latitude,
        maximal longitude and maximal latitude.
    """
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
    """
    This function logs into the USGS API and EarthExplorer with the provided
    username and password, searches for scenes of the Landsat satellite based
    on the provided parameters, optionally downloads each found scene, and
    then logs out of the USGS API and EarthExplorer. It previously varifys the
    input for 'max_results', 'max_cloud_cover', 'coordinates', 'start_date'
    and 'end_date'.

    Parameters:
        username (str): The username for the USGS API and EarthExplorer.
        password (str): The password for the USGS API and EarthExplorer.
        coordinates (List[Tuple[float, float]]): A list of tuples where each
            tuple represents a pair of latitude and longitude for one
            coordinate.
        start_date (str): The start date for the search in the
            format 'YYYY-MM-DD'.
        end_date (str): The end date for the search in the
            format 'YYYY-MM-DD'.
        output_dir (str): The directory where the downloaded scenes
            will be saved.
        max_cloud_cover (int): The maximum cloud cover percentage for
            the search. Default is 10
        max_results (int): The maximum number of results to return from
            the search. Default is 100.
        download (bool): Whether to download the found scenes.
            Default is True.

    Returns:
        None

    Raises:
        ValueError: If max_results is not between 0 and 50000.
        ValueError: If max_cloud_cover is not between 0 and 100.
        ValueError: If each coordinate is not a tuple of two elements.
        ValueError: If latitude or longitude value is invalid.
        ValueError: If start_date is not before end_date.
        ValueError: If at least one coordinate pair is not given.
    """
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
