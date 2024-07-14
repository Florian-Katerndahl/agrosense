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

from datetime import datetime as dt
from typing import List, Tuple

import json
import requests
import sys
import time
import argparse
import datetime
import threading
import re

maxthreads = 5  # Threads count for downloads
sema = threading.Semaphore(value=maxthreads)
label = datetime.datetime.now().strftime(
"%Y%m%d_%H%M%S"
)  # Customized label using date time
threads = []


# send http request
def sendRequest(url, data, apiKey=None):
    pos = url.rfind("/") + 1
    endpoint = url[pos:]
    json_data = json.dumps(data)

    if apiKey == None:
        response = requests.post(url, json_data)
    else:
        headers = {"X-Auth-Token": apiKey}
        response = requests.post(url, json_data, headers=headers)

    try:
        httpStatusCode = response.status_code
        if response == None:
            print("No output from service")
            sys.exit()
        output = json.loads(response.text)
        if output["errorCode"] != None:
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
        pos = serviceUrl.find("api")
        print(
            f"Failed to parse request {endpoint} response. Re-check the input {json_data}. The input examples can be found at {url[:pos]}api/docs/reference/#{endpoint}\n"
        )
        sys.exit()
    response.close()
    print(f"Finished request {endpoint} with request ID {output['requestId']}\n")

    return output["data"]


def downloadFile(url, path):
    sema.acquire()
    try:
        response = requests.get(url, stream=True)
        disposition = response.headers["content-disposition"]
        filename = re.findall("filename=(.+)", disposition)[0].strip('"')
        print(f"Downloading {filename} ...\n", file=sys.stderr)
        if path != "" and path[-1] != "/":
            filename = "/" + filename
        open(path + filename, "wb").write(response.content)
        print(f"Downloaded {filename}\n", file=sys.stderr)
        sema.release()
    except Exception as e:
        print(f"Failed to download from {url}. {e}. Will try to re-download.")
        sema.release()
        runDownload(threads, url, path)


def runDownload(threads, url, path):
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

def usgs_script(username: str, password: str,
            mbr: List[float],
            start_date: str, end_date: str, output_dir: str,
            max_cloud_cover: int = 10,
            max_results: int = 100) -> None:
    """
    copied from example script
    """    
    print("\nRunning Scripts...\n")

    serviceUrl = "https://m2m.cr.usgs.gov/api/api/json/stable/"

    # login
    payload = {"username": username, "password": password}

    apiKey = sendRequest(serviceUrl + "login", payload)

    print("API Key: " + apiKey + "\n")

    datasetName = "landsat_ot_c2_l2"

    spatialFilter = {
        "filterType": "mbr",
        "lowerLeft": {"latitude": mbr[1], "longitude": mbr[0]},
        "upperRight": {"latitude": mbr[3], "longitude": mbr[2]},
    }

    temporalFilter = {"start": start_date, "end": end_date}

    payload = {
        "datasetName": datasetName,
        "spatialFilter": spatialFilter,
        "temporalFilter": temporalFilter,
    }

    print("Searching datasets...\n")
    datasets = sendRequest(serviceUrl + "dataset-search", payload, apiKey)

    print("Found ", len(datasets), " datasets\n")

    # download datasets
    for dataset in datasets:
        # Because I've ran this before I know that I want GLS_ALL, I don't want to download anything I don't
        # want so we will skip any other datasets that might be found, logging it incase I want to look into
        # downloading that data in the future.
        if dataset["datasetAlias"] != datasetName:
            print("Found dataset " + dataset["collectionName"] + " but skipping it.\n")
            continue

        # I don't want to limit my results, but using the dataset-filters request, you can
        # find additional filters

        acquisitionFilter = temporalFilter

        payload = {
            "datasetName": dataset["datasetAlias"],
            "maxResults": max_results,
            "startingNumber": 1,
            "sceneFilter": {
                "spatialFilter": spatialFilter,
                "acquisitionFilter": acquisitionFilter,
                "cloudCoverFilter": {"min": 0, "max": max_cloud_cover, "includeUnknown": False}
            },
        }

        # Now I need to run a scene search to find data to download
        print("Searching scenes...\n\n")

        scenes = sendRequest(serviceUrl + "scene-search", payload, apiKey)

        # Did we find anything?
        if scenes["recordsReturned"] > 0:
            sceneIds = [result["entityId"] for result in scenes["results"]]
            payload = {"datasetName": dataset["datasetAlias"],
                       "entityIds": sceneIds}
            downloadOptions = sendRequest(
                serviceUrl + "download-options", payload, apiKey)

            downloads = [
                {"entityId": product["entityId"],
                 "productId": product["id"]}
                for product in downloadOptions
                if product["available"]]

            # Did we find products?
            if downloads:
                requestedDownloadsCount = len(downloads)
                # print("Found", requestedDownloadsCount, "downloads")
                # set a label for the download request
                label = datetime.datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )  # Customized label using date time
                payload = {"downloads": downloads, "label": label}
                # Call the download to get the direct download urls
                requestResults = sendRequest(
                    serviceUrl + "download-request", payload, apiKey
                )

                # PreparingDownloads has a valid link that can be used but data may not be immediately available
                # Call the download-retrieve method to get download that is available for immediate download
                if (
                    requestResults["preparingDownloads"] != None
                    and len(requestResults["preparingDownloads"]) > 0
                ):
                    payload = {"label": label}
                    moreDownloadUrls = sendRequest(
                        serviceUrl + "download-retrieve", payload, apiKey
                    )

                    downloadIds = []

                    for download in moreDownloadUrls["available"]:
                        if (
                            str(download["downloadId"]) in requestResults["newRecords"]
                            or str(download["downloadId"])
                            in requestResults["duplicateProducts"]
                        ):
                            downloadIds.append(download["downloadId"])
                            runDownload(threads, download["url"], output_dir)

                    for download in moreDownloadUrls["requested"]:
                        if (
                            str(download["downloadId"]) in requestResults["newRecords"]
                            or str(download["downloadId"])
                            in requestResults["duplicateProducts"]
                        ):
                            downloadIds.append(download["downloadId"])
                            runDownload(threads, download["url"], output_dir)

                    # Didn't get all of the reuested downloads, call the download-retrieve method again probably after 30 seconds
                    while len(downloadIds) < (
                        requestedDownloadsCount - len(requestResults["failed"])
                    ):
                        preparingDownloads = (
                            requestedDownloadsCount
                            - len(downloadIds)
                            - len(requestResults["failed"])
                        )
                        print(
                            "\n",
                            preparingDownloads,
                            "downloads are not available. Waiting for 30 seconds.\n",
                        )
                        time.sleep(30)
                        print("Trying to retrieve data\n")
                        moreDownloadUrls = sendRequest(
                            serviceUrl + "download-retrieve", payload, apiKey
                        )
                        for download in moreDownloadUrls["available"]:
                            if download["downloadId"] not in downloadIds and (
                                str(download["downloadId"])
                                in requestResults["newRecords"]
                                or str(download["downloadId"])
                                in requestResults["duplicateProducts"]
                            ):
                                downloadIds.append(download["downloadId"])
                                runDownload(threads, download["url"], output_dir)

                else:
                    # Get all available downloads
                    for download in requestResults["availableDownloads"]:
                        runDownload(threads, download["url"], output_dir)
        else:
            print("Search found no results.\n")

    print("Downloading files... Please do not close the program\n", file=sys.stderr)
    for thread in threads:
        thread.join()

    print("Complete Downloading")

    # Logout so the API Key cannot be used anymore
    endpoint = "logout"
    if sendRequest(serviceUrl + endpoint, None, apiKey) == None:
        print("Logged Out\n\n")
    else:
        print("Logout Failed\n\n")



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
    if (dt.strptime(start_date, "%Y-%m-%d")
            >= dt.strptime(end_date, "%Y-%m-%d")):
        raise ValueError("Error: The start_date must be before the end_date.")
    # Search and Download
    # login to API and EarthExplorer
    # api = API(username, password)
    # earth_explorer = EarthExplorer(username, password)
    # search depending on the number of coordinates
    if len(coordinates) == 1:
        # search for scenes if coordinates only contains one searching point
        raise RuntimeError
        # scenes = api.search(dataset="landsat_etm_c2_l2", start_date=start_date,
        #                     end_date=end_date,
        #                     max_cloud_cover=max_cloud_cover,
        #                     max_results=max_results,
        #                     latitude=coordinates[0][0],
        #                     longitude=coordinates[0][1])
    elif len(coordinates) >= 2:
        # get bounding box from coordinates
        bounding_box = get_bounding_box(coordinates)
        # search for scenes through a bounding box
        usgs_script(username, password, bounding_box, start_date, end_date, output_dir, max_cloud_cover, max_results)
    
