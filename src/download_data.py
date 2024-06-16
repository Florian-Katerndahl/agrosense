from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer

# Login to API and EarthExplorer
username = "RSE_P2_open"  # username for USGS account
password = "jerqez-kujKes-qopra0"  # password for USGS account
api = API(username, password)  # API instance for Log-In
earth_explorer = EarthExplorer(username, password)  # EarthExplorer instance for Log-In

# List of Locations (latitude, longitude) in Saudi-Arabia
locations = [ 
    (24.77, 46.74)]  # Riad
    #(21.49, 39.19),  # Jeddah
    #(21.39, 39.86),  # Mecca
    #(24.47, 39.61)]  # Medina

# Search for data in all locations
for latitude, longitude in locations:
    # Search within two different datasets and time periods
    """
    Landsat 5 TM Collection 2 was active from 1984-2013. Landsat 7 ETM+ Collection 2 started 1999 and is still active. For both datasets Level 2 
    was chosen as it includes additional corrections to remove atmospheric effects. The irrigation project started in the 1970s (surely since 1976) 
    but the first satellite only launched later.
    """
    for dataset, start_date, end_date in [('landsat_tm_c2_l2', '1985-01-01', '1999-12-31'), ('landsat_etm_c2_l2', '2000-01-01', '2020-12-31')]:
        scenes = api.search(
            dataset=dataset,
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date,
            max_cloud_cover=10)  # maximum cloud coverage of 10% to assure clear detection
            # bbox=[16.6, 34.5, 32.3, 55.7])  # coordinates of bounding box to cover Saudi-Arabia fully
        
        print(f'{len(scenes)} scenes for the location ({latitude}, {longitude}) were found. \n [{dataset}, {start_date}, {end_date}]')
        for scene in scenes:
            print(scene['acquisition_date'].strftime('%Y-%m-%d'))
            # download the found scenes
            earth_explorer.download(scene['entity_id'], output_dir='./data')
            """
            2018-05-31 Landsat 7 ETM+ Collection 2 Level 2
            landsat_product_id 'LE07_L2SP_166043_20180531_20200829_02_T1' (failed with dataset id 1 of 3. Re-trying with the next one.) = 477M
            entity_id 'LE71660432018151NPA00' (failed with dataset id 1 of 2. Re-trying with the next one.) = 288M ||| worked
            display_id 'LE07_L2SP_166043_20180531_20200829_02_T1' (not tried)
            landsat_scene_id 'LE71660432018151NPA00' (not tried)
            """

# Logout of API and EarthExplorer
api.logout()
earth_explorer.logout()
