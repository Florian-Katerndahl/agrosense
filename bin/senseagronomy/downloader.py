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

from datetime import datetime as dt
from typing import List, Tuple

import os
import json
import requests
import sys
import time
import datetime
import threading
import re

maxthreads = 5  # Threads count for downloads
sema = threading.Semaphore(value=maxthreads)
label = datetime.datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)  # Customized label using date time
threads = []


def sendRequest(url, data, apiKey=None):
    """
    This functions sends an HTTP POST request to the specified url with the
    given data.

    Parameters:
        url (str): The URL to which the request is sent.
        data (dict): The data to be sent in the request.
        apiKey (str): The API key for authentication. If None, no
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

    if apiKey is None:
        response = requests.post(url, json_data)
    else:
        headers = {"X-Auth-Token": apiKey}
        response = requests.post(url, json_data, headers=headers)

    try:
        httpStatusCode = response.status_code
        if response is None:
            print("No output from service")
            sys.exit()
        output = json.loads(response.text)
        if output["errorCode"] is not None:
            print("Failed Request ID", output["requestId"])
            print(output["errorCode"], "-", output["errorMessage"])
            sys.exit()
        if httpStatusCode == 404:
            print("404 Not Found")
            sys.exit()
        elif httpStatusCode == 401:
            print("401 Unauthorized")
            sys.exit()
        elif httpStatusCode == 400:
            print("Error Code", httpStatusCode)
            sys.exit()
    except Exception as e:
        response.close()
        pos = url.find("api")
        print(
            f"Failed to parse request {endpoint} response. "
            f"Re-check the input {json_data}. "
            f"The input examples can be found at "
            f"{url[:pos]}api/docs/reference/#{endpoint}\n"
        )
        sys.exit()
    response.close()
    print(
        f"Finished request {endpoint} "
        f"with request ID {output['requestId']}\n"
    )

    return output["data"]


def downloadFile(url, path):
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
        This function uses a semaphore (sema) to limit the number of
        concurrent downloads. It acquires the semaphore before starting
        the downlaod and releases if after the download is finished,
        regardless of whether the download was successful or not.
    """
    sema.acquire()
    try:
        response = requests.get(url, stream=True)
        disposition = response.headers["content-disposition"]
        filename = re.findall("filename=(.+)", disposition)[0].strip('"')
        print(f"Downloading {filename} ...\n", file=sys.stderr)
        if path and not path.endswith("/"):
            path += "/"
        with open(path + filename, "wb") as file:
            file.write(response.content)
        print(f"Downloaded {filename}", file=sys.stderr)
    except Exception as e:
        print(f"Failed to download from {url}. {e}. Will try to re-download.")
        runDownload(threads, url, path)
    finally:
        sema.release()


def runDownload(threads, url, path):
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
    thread = threading.Thread(target=downloadFile, args=(url, path,))
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


def usgs_script(
    username: str,
    password: str,
    mbr: List[float],
    start_date: str,
    end_date: str,
    output_dir: str,
    max_cloud_cover: int = 10,
    max_results: int = 100
) -> None:

    """
    copied from example script
    """
    print("\nRunning Scripts...\n")

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
    serviceUrl = "https://m2m.cr.usgs.gov/api/api/json/stable/"

    apiKey = sendRequest(serviceUrl + "login",
                         {"username": username, "password": password})
    print("API Key: " + apiKey + "\n")

    spatialFilter = {"filterType": "mbr",
                     "lowerLeft": {"latitude": mbr[1], "longitude": mbr[0]},
                     "upperRight": {"latitude": mbr[3], "longitude": mbr[2]}}
    temporalFilter = {"start": start_date, "end": end_date}
    datasetName = "landsat_ot_c2_l2"

    payload = {"datasetName": datasetName, "spatialFilter": spatialFilter,
               "temporalFilter": temporalFilter}
    print("Searching datasets...\n")
    datasets = sendRequest(serviceUrl + "dataset-search", payload, apiKey)

    print("Found ", len(datasets), " datasets\n")
    # download datasets
    for dataset in datasets:
        if dataset["datasetAlias"] != datasetName:
            print("Found dataset " + dataset["collectionName"] +
                  " but skipping it.\n")
            continue

        acquisitionFilter = temporalFilter
        payload = {"datasetName": dataset["datasetAlias"],
                   "maxResults": max_results, "startingNumber": 1,
                   "sceneFilter": {"spatialFilter": spatialFilter,
                                   "acquisitionFilter": acquisitionFilter,
                                   "cloudCoverFilter":
                                   {"min": 0, "max": max_cloud_cover,
                                    "includeUnknown": False}}}

        payload = {
            "datasetName": dataset["datasetAlias"],
            "maxResults": max_results,
            "startingNumber": 1,
            "sceneFilter": {
                "spatialFilter": spatialFilter,
                "acquisitionFilter": acquisitionFilter,
                "cloudCoverFilter": {
                    "min": 0,
                    "max": max_cloud_cover,
                    "includeUnknown": False
                }
            },
        }

        # Now I need to run a scene search to find data to download
        print("Searching scenes...\n\n")
        scenes = sendRequest(serviceUrl + "scene-search", payload, apiKey)

        if scenes["recordsReturned"] > 0:
            sceneIds = [result["entitiyId"] for result in scenes["results"]]
            payload = {"datasetName": dataset["datasetAlias"],
                       "entityIds": sceneIds}
            downloadOptions = sendRequest(
                serviceUrl + "download-options", payload, apiKey)

            downloads = [
                {"entitiyId": product["entitiyId"],
                 "productId": product["id"]}
                for product in downloadOptions
                if product["available"]]

            if downloads:
                label = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                payload = {"downloads": downloads, "label": label}
                requestResults = sendRequest(
                    serviceUrl + "download-request", payload, apiKey)

                if requestResults.get("preparingDownloads"):
                    payload = {"label": label}
                    moreDownloadUrls = sendRequest(
                        serviceUrl + "download-retrieve", payload, apiKey)
                    downloadIds = []

                    for download in moreDownloadUrls["available"]:
                        if (
                            str(download["downloadId"])
                            in requestResults["newRecords"]
                            or str(download["downloadId"])
                            in requestResults["duplicateProducts"]
                        ):
                            downloadIds.append(download["downloadId"])
                            runDownload(threads, download["url"], output_dir)

                    for download in moreDownloadUrls["requested"]:
                        if (
                            str(download["downloadId"])
                            in requestResults["newRecords"]
                            or str(download["downloadId"])
                            in requestResults["duplicateProducts"]
                        ):
                            downloadIds.append(download["downloadId"])
                            runDownload(threads, download["url"], output_dir)

                    # Didn't get all of the reuested downloads, call the
                    # download-retrieve method again probably after 30 seconds
                    while len(downloadIds) < (
                        len(downloads) - len(requestResults["failed"])
                    ):
                        time.sleep(30)
                        print("Trying to retrieve data\n")
                        moreDownloadUrls = sendRequest(
                            serviceUrl + "download-retrieve", payload, apiKey)
                        for download in moreDownloadUrls["available"]:
                            if download["downloadId"] not in downloadIds:
                                downloadIds.append(download["downloadId"])
                                runDownload(
                                    threads,
                                    download["url"],
                                    output_dir
                                )

                else:
                    # Get all available downloads
                    for download in requestResults["availableDownloads"]:
                        runDownload(threads, download["url"], output_dir)
        else:
            print("Search found no results.\n")

    print("Downloading files... Please do not close the program\n",
          file=sys.stderr)
    for thread in threads:
        thread.join()

    print("Complete Downloading")

    # Logout so the API Key cannot be used anymore
    endpoint = "logout"
    if sendRequest(serviceUrl + endpoint, None, apiKey) is None:
        print("Logged Out\n\n")
    else:
        print("Logout Failed\n\n")


def validate_and_download_data(
    username: str,
    password: str,
    coordinates: List[Tuple[float, float]],
    start_date: str,
    end_date: str,
    output_dir: str,
    max_cloud_cover: int = 10,
    max_results: int = 100,
    download: bool = True
) -> None:
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
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
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
