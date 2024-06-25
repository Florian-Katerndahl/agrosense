from argparse import ArgumentParser
from downloader import search_and_download_data
from typing import List, Tuple


def main() -> None: 
    parser = ArgumentParser(
        description="This program is used to search and download Landsat images using landsatxplore."
        "It requires the username and password from an USGS account."
    )
    parser.add_argument(
        "--username", 
        type=str, 
        required=True, 
        help="Your USGS username."
    )

    parser.add_argument(
        "--password", 
        type=str,
        required=True,
        help="Your USGS password."
    )
    parser.add_argument(
        "--coordinates",
        type=float,
        required=True,
        nargs="+",
        help="Coordinates for your chosen area in the format latitude_1 longitude_1 latitude_2 longitude_2 ..."
    )
    parser.add_argument(
        "--start-date",
        type=str,
        required=False, 
        help="Enter the start date in the format YYYY-MM-DD."
    )
    parser.add_argument(
        "--end-date",
        type=str,
        required=False,
        help="Enter the end date in the format YYYY-MM-DD."
    )
    parser.add_argument(
        "--max-cloud-cover", 
        type=int,
        required=False, 
        help="The maximum cloud cover percentage (0-100%)."
    )
    parser.add_argument(
        "--max-results", 
        type=int,
        required=False,
        help="The number of maximal resulting scenes (0-50000)."
    )
    parser.add_argument(
        "--output-dir",
        type=str, 
        required=False,
        help="Your output directory to store the downloaded scenes."
    )

    args = parser.parse_args()

    coordinates: List[Tuple[float, float]] = [(args.coordinates[i], args.coordinates[i + 1]) for i in range(0, len(args.coordinates),2)]

    search_and_download_data(args.username, args.password, coordinates, args.start_date, args.end_date, args.max_cloud_cover, args.max_results, args.output_dir)
