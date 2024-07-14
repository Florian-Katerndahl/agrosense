#!/usr/bin/env python3

"""
This script contains three functions: 'send_request', 'download_file',
'run_download', 'get_credentials', 'get_bounding_box',
'search_and_download_data' and 'validate_and_download_data'.

'send_request' sends a request to a specified URL with the given data and
optionally includes an API key for authentication.

'download_file' downloads a file from a specified URL and saves it to a given
path.

'run_download' starts a new thread to download a file from the specified URL
and saves it to the given path.

'get_credentials' is responsible for obtainting the username and password
either from the arguments passed or from the environment variables.

'get_bounding_box' calculates the bounding box for a given list of
coordinates.

'search_and_download_data' logs into the USGS API with the provided
credentials, performs a search based on the specified parameters, and
downloads the found scenes.

'validate_and_download_data' validates the input parameters and then uses
them to search and download data from the USGS API.
"""

from datetime import datetime as dt
from typing import List, Tuple

import os
import json
import sys
import time
import datetime
import threading
import re
import requests


MAXTHREADS = 5  # number if threads for download
SEMA = threading.Semaphore(value=MAXTHREADS)
THREADS = []
TIMEOUT = 30


def send_request(url, data, api_key=None):
    """
    This functions sends an HTTP POST request to the specified url with the
    given data.

    Parameters:
        url (str): The URL to which the request is sent.
        data (dict): The data to be sent in the request.
        api_key (str): The API key for authentication. If None, no
                      authentication is used. Optional.

    Returns:
        dict: The data from the response of the request.

    Raises:
        SystemExit: Exits the program if an error occurs or if the HTTP status
                    code indicates an error.

    Note:
        Outputs various error and status messages depending on the result of
        the request.
    """
    pos = url.rfind("/") + 1
    endpoint = url[pos:]
    json_data = json.dumps(data)

    if api_key is None:
        response = requests.post(url, json_data, timeout=TIMEOUT)
    else:
        headers = {"X-Auth-Token": api_key}
        response = requests.post(url, json_data, headers=headers,
                                 timeout=TIMEOUT)

    try:
        http_status_code = response.status_code
        if response is None:
            print("No output from service")
            sys.exit()
        output = json.loads(response.text)
        if output["errorCode"] is not None:
            print("Failed Request ID", output["requestId"])
            print(output["errorCode"], "-", output["errorMessage"])
            sys.exit()
        if http_status_code == 404:
            print("404 Not Found")
            sys.exit()
        elif http_status_code == 401:
            print("401 Unauthorized")
            sys.exit()
        elif http_status_code == 400:
            print("Error Code", http_status_code)
            sys.exit()
    except requests.exceptions.RequestException as e:
        response.close()
        pos = url.find("api")
        print(f"Failed to parse request {endpoint} response due to error "
              f"{e}. Re-check the input {json_data}. The input examples can "
              f"be found at {url[:pos]}api/docs/reference/#{endpoint}\n")
        sys.exit()
    response.close()
    print(f"Finished request {endpoint} with request ID "
          f"{output['requestId']}\n")

    return output["data"]


def download_file(url, path):
    """
    This function downloads a file from the specified URL and saves
    it to the given path.

    Parameters:
        url (str): The URL of the file to be downloaded.
        path (str): The path where the downloaded file will be saved.

    Raises:
        Exception: If there is an error during the download process, it will
                   try to re-download the file.

    Note:
        This function uses a semaphore (SEMA) to limit the number of
        concurrent downloads. It acquires the semaphore before starting
        the downlaod and releases if after the download is finished,
        regardless of whether the download was successful or not.
    """
    try:
        with SEMA:
            response = requests.get(url, stream=True, timeout=TIMEOUT)
            disposition = response.headers["content-disposition"]
            filename = re.findall("filename=(.+)", disposition)[0].strip('"')
            print(f"Downloading {filename} ...\n", file=sys.stderr)
            if path and not path.endswith("/"):
                path += "/"
            with open(path + filename, "wb") as file:
                file.write(response.content)
            print(f"Downloaded {filename}", file=sys.stderr)
    except requests.exceptions.RequestException as e:
        print(f"Failed to download from {url}. {e}. Will try to re-download.")
        run_download(THREADS, url, path)


def run_download(threads, url, path):
    """
    This function start a new thread to download a file from the specified URL
    and saves it to the given path.

    Parameters:
        threads (list): A list of threads. The new thread will be appended
                        to this list.
        url (str): The URL of the file to be downloaded.
        path (str): The path where the downloaded file will be saved.

    Note:
        Through the use of the threading module multiple downloads occuring
        concurrently is allowed.
    """
    thread = threading.Thread(target=download_file, args=(url, path,))
    threads.append(thread)
    thread.start()


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
                             mbr: List[float], start_date: str,
                             end_date: str, output_dir: str,
                             max_cloud_cover: int = 10,
                             max_results: int = 100) -> None:
    """
    This function downloads Landsat datasets from the USGS API within a
    specified date range, cloud cover limit, and geographical bounding box.

    Parameters:
        username (str): The username for the USGS API.
        password (str): The password for the USGS API.
        mbr (List[float]): The minimum bounding rectangle (MBR) for the
                           geographical area of interest.
        start_date (str): The start date for the date range filter in
                          the format 'YYYY-MM-DD'.
        end_date (str): The end date for the date range filter in the
                        format 'YYYY-MM-DD'.
        output_dir (str): The directory where the downloaded files
                          will be saved.
        max_cloud_cover (int): The maximum cloud cover percentage for the
                               scenes. Defaults to 10. Optional.
        max_results (int): The maximum number of scenes to download.
                           Defaults to 100. Optional.

    Returns:
        None
    """
    service_url = "https://m2m.cr.usgs.gov/api/api/json/stable/"

    api_key = send_request(service_url + "login",
                           {"username": username, "password": password})
    print("API Key: " + api_key + "\n")

    spatial_filter = {"filterType": "mbr",
                      "lowerLeft": {"latitude": mbr[1], "longitude": mbr[0]},
                      "upperRight": {"latitude": mbr[3], "longitude": mbr[2]}}
    temporal_filter = {"start": start_date, "end": end_date}
    dataset_name = "landsat_ot_c2_l2"

    payload = {"datasetName": dataset_name, "spatialFilter": spatial_filter,
               "temporalFilter": temporal_filter}
    print("Searching datasets...\n")
    datasets = send_request(service_url + "dataset-search", payload, api_key)

    print("Found ", len(datasets), " datasets\n")
    # download datasets
    for dataset in datasets:
        if dataset["datasetAlias"] != dataset_name:
            print("Found dataset " + dataset["collectionName"] +
                  " but skipping it.\n")
            continue

        acquisition_filter = temporal_filter
        payload = {"datasetName": dataset["datasetAlias"],
                   "maxResults": max_results, "startingNumber": 1,
                   "sceneFilter": {"spatialFilter": spatial_filter,
                                   "acquisitionFilter": acquisition_filter,
                                   "cloudCoverFilter":
                                   {"min": 0, "max": max_cloud_cover,
                                    "includeUnknown": False}}}

        print("Searching scenes...\n\n")
        scenes = send_request(service_url + "scene-search", payload, api_key)

        if scenes["recordsReturned"] > 0:
            scene_ids = [result["entityId"] for result in scenes["results"]]
            payload = {"datasetName": dataset["datasetAlias"],
                       "entityIds": scene_ids}
            download_options = send_request(
                service_url + "download-options", payload, api_key)

            downloads = [
                {"entityId": product["entityId"],
                 "productId": product["id"]}
                for product in download_options
                if product["available"]]

            if downloads:
                label = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                payload = {"downloads": downloads, "label": label}
                request_results = send_request(
                    service_url + "download-request", payload, api_key)

                if request_results.get("preparingDownloads"):
                    payload = {"label": label}
                    more_download_urls = send_request(
                        service_url + "download-retrieve", payload, api_key)
                    download_ids = []

                    for download in (
                        more_download_urls["available"] +
                        more_download_urls["requested"]
                    ):
                        if (
                            str(download["downloadId"]) in
                            request_results["newRecords"] or
                            str(download["downloadId"]) in
                            request_results["duplicateProducts"]
                        ):
                            download_ids.append(download["downloadId"])
                            run_download(THREADS, download["url"], output_dir)

                    # recall the download-retrieve method
                    while (len(download_ids) <
                           (len(downloads) - len(request_results["failed"]))):
                        time.sleep(30)
                        print("Trying to retrieve data\n")
                        more_download_urls = send_request(
                            service_url + "download-retrieve", payload,
                            api_key)
                        for download in more_download_urls["available"]:
                            if download["downloadId"] not in download_ids:
                                download_ids.append(download["downloadId"])
                                run_download(THREADS, download["url"],
                                             output_dir)

                else:
                    # Get all available downloads
                    for download in request_results["availableDownloads"]:
                        run_download(THREADS, download["url"], output_dir)
        else:
            print("Search found no results.\n")

    print("Downloading files... Please do not close the program\n",
          file=sys.stderr)
    for thread in THREADS:
        thread.join()

    print("Complete Downloading")

    # Logout so the API Key cannot be used anymore
    endpoint = "logout"
    if send_request(service_url + endpoint, None, api_key) is None:
        print("Logged Out\n\n")
    else:
        print("Logout Failed\n\n")


def validate_and_download_data(username: str, password: str,
                               coordinates: List[Tuple[float, float]],
                               start_date: str, end_date: str,
                               output_dir: str,
                               max_cloud_cover: int = 10,
                               max_results: int = 100) -> None:
    """
    This function validates the input parameters and then uses them to search
    and download data from the USGS API.

    Parameters:
        username (str): The username for USGS.
        password (str): The password for USGS.
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
            the search. Default is 10. Optional
        max_results (int): The maximum number of results to return from
            the search. Default is 100. Optional

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
        if (
            -90 > latitude or latitude > 90 or
            -180 > longitude or longitude > 180
        ):
            raise ValueError("Error: Invalid latitude or longitude value.")
    # check whether start_date is before end_date
    if (dt.strptime(start_date, "%Y-%m-%d")
            >= dt.strptime(end_date, "%Y-%m-%d")):
        raise ValueError("Error: The start_date must be before the end_date.")

    # Search and Download
    if len(coordinates) >= 2:
        # get bounding box from coordinates
        bounding_box = get_bounding_box(coordinates)
        search_and_download_data(username, password, bounding_box, start_date,
                                 end_date, output_dir, max_cloud_cover,
                                 max_results)
    else:
        raise ValueError("At least two coordinates are required.")
