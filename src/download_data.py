from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer

# login to API and EarthExplorer
username = "RSE_P2_open"  # username for USGS account
password = "jerqez-kujKes-qopra0"  # password for USGS account
api = API(username, password)  # API instance for Log-In
earth_explorer = EarthExplorer(username, password)  # EarthExplorer instance for Log-In

# coordinates for polygon defining the chosen area around Haradh
coordinates = [(24.5646, 49.0965), (24.5046, 49.4907), (24.2269, 49.4591), (24.0176, 49.4501), (23.9354, 49.3671), 
               (23.7137, 49.3753), (23.4935, 49.2579), (23.2956, 49.4501), (23.1479, 49.440), (22.9887, 49.5126), 
               (22.8445, 49.2737), (22.9230, 49.1226), (23.0696, 49.1364), (23.1883, 48.8589), (23.4506, 48.8644), 
               (23.5917, 48.9771), (23.8959, 48.6530), (24.2920, 48.6530), (24.6046, 48.8727)]

# defining the bounding box out of the coordinates
latitudes = [coordinate[0] for coordinate in coordinates]
longitudes = [coordinate[1] for coordinate in coordinates]
bounding_box = [min(longitudes), min(latitudes), max(longitudes), max(latitudes)] # [48.653, 22.8445, 49.5126, 24.6046]

# Search for data within two different datasets for the time period 2015-01-01 until 2020-12-31
"""
We chose the Landsat 8/9 Collection 2, that started in 2013 and is still active. For this satellite there are 439 scenes found for the chosen area and time period.
For the dataset Level 2 was chosen as it includes additional corrections to remove atmospheric effects.
Landsat 5 and 9 were/are active previously or afterwards our chosen timeslot. 
Landsat 7 ETM+ Collection 2 has some technical issues since 2019 and due to data storage space we decided to only choose one dataset.
"""
scenes = api.search(
    max_results = 1000, 
    dataset = 'landsat_ot_c2_l2', 
    start_date = '2015-01-01', 
    end_date = '2020-12-31', 
    max_cloud_cover = 10, # maximum cloud coverage of 10% to assure clear detection
    bbox = bounding_box)

# downloading each found scene
for scene in scenes:
    earth_explorer.download(scene['landsat_product_id'], output_dir='./data')

# Logout of API and EarthExplorer
api.logout()
earth_explorer.logout()
