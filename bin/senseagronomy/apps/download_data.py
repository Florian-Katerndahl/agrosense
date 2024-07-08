"""
This script contains the 'main' function which is the entry point of the
program.

The 'main' function parses command line arguments, retrieves the necessary
credentials, validates coordinates, and invokes the search and download of
the data. The program utilizes landsatxplore to search for and download
Landsat 8/9 Collection 2 Level 2 images.
"""

from argparse import ArgumentParser
from senseagronomy.downloader import search_and_download_data, get_credentials
from typing import List, Tuple


def main() -> int:
    """
    This function runs the program. It parses command line arguments,
    retrieves credentials, validates coordinates, and calls the function
    to search and download Landsat images using landsatxplore.

    Command line arguments:
        --username: Your USGS username. Optional.
        --password: Your USGS password. Optional.
        --coordinates: Coordinates for the chosen area. Required.
        --start-date: The start date for the search in the format
                      YYYY-MM-DD. Optional.
        --end-date: The end date for the search in the format
                    YYYY-MM-DD. Optional.
        --max-cloud-cover: The maximum cloud cover percentage (0-100%).
                           Optional.
        --max-results: The number of maximal resulting scenes (0-50000).
                       Optional.
        --output-dir: The output directory to store the downloaded scenes.
                      Optional.
        --download: Whether the user wants to download the found scenes.
                    Default is True.

    Returns:
        int: Returns 0 if the program runs successfully.

    Raises:
        ValueError: If either a latitude or longitude variable of a given
                    coordinate is missing.
        ValueError: If at least one coordinate is not given.
    """
    # create command line parser
    parser = ArgumentParser(
        description="This program is used to search and download Landsat"
        " images using landsatxplore. It requires the username and password"
        " from an USGS account. Only data from Landsat 8/9 Collection 2"
        " Level 2 can be searched and downloaded. Landsat 9 started on the"
        " 27th of September 2021, whereas Landsat 8 started on the 11th of"
        " February 2013 and both are still active.")
    # add command line arguments
    parser.add_argument(
        "--username",
        type=str,
        required=False,
        help="Your USGS username.")
    parser.add_argument(
        "--password",
        type=str,
        required=False,
        help="Your USGS password.")
    parser.add_argument(
        "--coordinates",
        type=float,
        required=True,
        nargs="+",
        help="Coordinates for the chosen area in the format latitude_1 "
             "longitude_1 latitude_2 longitude_2 ...")
    parser.add_argument(
        "--start-date",
        type=str,
        required=False,
        help="Enter the start date in the format YYYY-MM-DD.")
    parser.add_argument(
        "--end-date",
        type=str,
        required=False,
        help="Enter the end date in the format YYYY-MM-DD.")
    parser.add_argument(
        "--max-cloud-cover",
        type=int,
        required=False,
        help="The maximum cloud cover percentage (0-100%).")
    parser.add_argument(
        "--max-results",
        type=int,
        required=False,
        help="The number of maximal resulting scenes (0-50000).")
    parser.add_argument(
        "--output-dir",
        type=str,
        required=False,
        help="Your output directory to store the downloaded scenes.")
    parser.add_argument(
        "--download",
        type=bool,
        required=False,
        default=True,
        help="Whether to download the found scenes. Default is True.")

    args = parser.parse_args()

    # retrieve credentials
    username, password = get_credentials(args)
    # validate coordinates
    try:
        coordinates: List[Tuple[float, float]] = [
            (args.coordinates[i], args.coordinates[i + 1])
            for i in range(0, len(args.coordinates), 2)]
    except IndexError:
        raise ValueError("Error: Either a latitude or longitude variable"
                         " of a given coordinate is misssing.")
    if len(args.coordinates) <= 1:
        raise ValueError("Error: At least one coordinate containing of"
                         " longitude and latitude has to be given.")
    # search and download the Landsat scenes
    search_and_download_data(username, password, coordinates, args.start_date,
                             args.end_date, args.output_dir,
                             max_cloud_cover=args.max_cloud_cover,
                             max_results=args.max_results,
                             download=args.download)

    return 0


if __name__ == "__main__":
    main()
