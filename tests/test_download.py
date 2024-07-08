#!/usr/bin/env python3

"""
This module contains unit tests for the functions in 'downloader.py', as well
as the 'main'-function in 'download_data.py'

It uses pytest for the testing framework and pytest-mock to mock
objects and functions. The functions tested are 'get_credentials',
'get_bounding_box', 'search_and_download_data', 'main'.

For the function 'get_bounding_box' it is neither tested if an empty list
or list containing empty tuples is given as input, whether the given
coordinates contain an invalid latitude or longitude variable or a
coordinate is missing either the latitude or longitude variable, because those
cases are covered within the function 'search_and_download_data' or the 'main'
function from download_data.py.
"""

import collections
import pytest

from bin.download.downloader import *
from bin.download.download_data import *


# Testing the 'get_credentials' function
def test_get_credentials_from_args(mocker):
    """
    Test the 'get_credentials' function with a username and password provided
    in the arguments.
    """
    Args = collections.namedtuple('Args', ['username', 'password'])
    args = Args(username='test_username', password='test_password')
    mocker.patch('downloader.os.environ.get', return_value=None)
    username, password = get_credentials(args)
    assert username == 'test_username'
    assert password == 'test_password'


def test_get_credentials_from_env(mocker):
    """
    Test the 'get_credentials' function with a username and password provided
    as environment variables.
    """
    Args = collections.namedtuple('Args', ['username', 'password'])
    args = Args(username=None, password=None)
    mocker.patch('downloader.os.environ.get',
                 side_effect=['env_username', 'env_password'])
    username, password = get_credentials(args)
    assert username == 'env_username'
    assert password == 'env_password'


def test_get_credentials_differently_set(mocker):
    """
    Test the 'get_credentials' function if the username is provided in
    arguments, but the password is provided in environment variables. The
    function behaves the same if password is provided in arguments and
    username in environment variables.
    """
    Args = collections.namedtuple('Args', ['username', 'password'])
    args = Args(username='test_username', password=None)
    mocker.patch('downloader.os.environ.get', side_effect=['env_password'])
    username, password = get_credentials(args)
    assert username == 'test_username'
    assert password == 'env_password'


def test_get_credentials_none_set(mocker):
    """
    Test the 'get_credentials' function if neither username or password is
    provided in arguments or environment variables.
    """
    Args = collections.namedtuple('Args', ['username', 'password'])
    args = Args(username=None, password=None)
    mocker.patch('downloader.os.environ.get', return_value=None)
    with pytest.raises(ValueError):
        get_credentials(args)


def test_get_credentials_missing_one(mocker):
    """
    Test the 'get_credentials' function with no username provided in arguments
    or environment variables. The function behaves the same if no password is
    provided in arguments or environment variables. Whether the one variable
    that is set is provided in arguments or environment doesn't influence the
    functions output.
    """
    Args = collections.namedtuple('Args', ['username', 'password'])
    args = Args(username=None, password='test_password')
    mocker.patch('downloader.os.environ.get', return_value=None)
    with pytest.raises(ValueError):
        get_credentials(args)


# Testing the 'get_bounding_box' function
def test_get_bounding_box_four_coordinates():
    """
    Test the `get_bounding_box` function with a list of four coordinates.
    """
    coordinates = [(40.7128, -74.0060), (34.0522, -118.2437)]
    result = get_bounding_box(coordinates)
    assert result == [-118.2437, 34.0522, -74.0060, 40.7128]


def test_get_bounding_box_more_coordinates():
    """
    Test the `get_bounding_box` function with a list of coordinates containing
    more than four coordinates.
    """
    coordinates = [(40.7128, -74.0060), (34.0522, -118.2437),
                   (37.7012, -122.2530), (52.3906, 13.0645)]
    result = get_bounding_box(coordinates)
    assert result == [-122.2530, 34.0522, 13.0645, 52.3906]


# Testing the 'search_and_download_data' function
@pytest.mark.parametrize(
    "coordinates, expected",
    [([], ValueError), ([(40.7128,)], ValueError),
     ([(100.0, -74.0060)], ValueError), ([(40.7128, 200.0)], ValueError),],)
def test_search_and_download_data_coordinates(mocker, coordinates, expected):
    """
    Test the 'search_and_download_data' function for the valid coordinates.
    Cases are an empty list, one missing latitude/longitude variable and an
    invalid latitude/longitude variable.
    """
    mock_api = mocker.patch('downloader.API')
    mock_earth_explorer = mocker.patch('downloader.EarthExplorer')
    mock_api.return_value.search.return_value = ['scene1', 'scene2', 'scene3']
    mock_earth_explorer.return_value.download.return_value = None
    if issubclass(expected, Exception):
        with pytest.raises(expected):
            search_and_download_data('test_username', 'test_password',
                                     coordinates, '2022-01-01', '2022-12-31',
                                     '/path/to/output', 10, 10, True)
    else:
        search_and_download_data('test_username', 'test_password',
                                 coordinates, '2022-01-01', '2022-12-31',
                                 '/path/to/output', 10, 10, True)


def test_search_and_download_data_download_option(mocker):
    """
    Test the 'search_and_download_data' function to ensure the download option
    works correctly. If 'download=True' the download method should be called,
    whereas it shouldn't if 'download=False'.
    """
    mock_api = mocker.patch('downloader.API')
    mock_earth_explorer = mocker.patch('downloader.EarthExplorer')
    mock_api.return_value.search.return_value = [
        {'landsat_product_id': 'scene1'}, {'landsat_product_id': 'scene2'}]
    mock_earth_explorer.return_value.download.return_value = None
    search_and_download_data('username', 'password', [(0, 0)], '2022-01-01',
                             '2022-12-31', '/path/to/output', download=True)
    assert mock_earth_explorer.return_value.download.called
    mock_earth_explorer.return_value.download.reset_mock()
    search_and_download_data('username', 'password', [(0, 0)], '2022-01-01',
                             '2022-12-31', '/path/to/output', download=False)
    assert not mock_earth_explorer.return_value.download.called


def test_search_and_download_data_date_range(mocker):
    """
    Test the 'search_and_download_data' function with a date range before the
    11th of February 2013.
    """
    mock_api = mocker.patch('downloader.API')
    mock_earth_explorer = mocker.patch('downloader.EarthExplorer')
    mock_print = mocker.patch('builtins.print')
    mock_api.return_value.search.return_value = []
    mock_earth_explorer.return_value.download.return_value = None
    search_and_download_data('username', 'password', [(0, 0)], '1990-12-31',
                             '1999-12-31', '/path/to/output')
    mock_print.assert_called_once_with('Found 0 scenes.')


def test_search_and_download_data_integer_ranges(mocker):
    """
    Test the 'search_and_download_data' function for 'max_results' and
    'max_cloud_cover' with values out of the allowed range.
    """
    with pytest.raises(ValueError) as e:
        search_and_download_data('username', 'password', [(0, 0)],
                                 '2022-01-01', '2022-12-31',
                                 '/path/to/output', max_cloud_cover=101)
    assert str(e.value) == 'Error: max_cloud_cover should be between 0-100%.'
    with pytest.raises(ValueError) as e:
        search_and_download_data('username', 'password', [(0, 0)],
                                 '2022-01-01', '2022-12-31',
                                 '/path/to/output', max_results=50001)
    assert str(e.value) == 'Error: max_results should be set between 0-50.000.'


def test_search_and_download_data_start_before_end_date():
    """
    Test the 'search_and_download_data' function with a 'start_date'
    that is after the 'end_date'.
    """
    with pytest.raises(ValueError) as e:
        search_and_download_data('username', 'password', [(0, 0)],
                                 '2022-12-31', '2022-01-01',
                                 '/path/to/output')
    assert str(e.value) == 'Error: The start_date must be before the end_date.'


# Test the 'main' function
@pytest.mark.parametrize(
    "coordinates, expected",
    [([40.7128], ValueError), ([], ValueError)])
def test_main_coordinate_validation(coordinates, expected):
    args = {'coordinates': coordinates}
    with pytest.raises(ValueError) as e:
        search_and_download_data('username', 'password', args, '2022-01-01',
                                 '2022-12-31', '/path/to/output')
