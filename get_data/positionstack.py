"""
Script to retrieve geographic data of all locations via the Positionstack API.
"""


import pandas as pd
from tqdm import tqdm
import requests
import os
import concurrent.futures
from get_data.arguments import parse_directory
from get_data import config


def main(directory):
    """Retrieves geographical data for all locations.

    Parameters
    ----------
    directory: str
        path to the folder where the data of all job ads are stored
    """
    try:
        df = pd.read_csv(os.path.join(directory, "data_long.csv"))
    except FileNotFoundError:
        print("Needed Data was not found in directory.")
    else:
        print("get geo data")
        api_key = config.positionstack_key
        locations = df["location"].unique()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            geo_data = list(tqdm(executor.map(lambda x: get_location(x, api_key), locations), total=len(locations)))
        geo_data = pd.concat(geo_data)
        geo_data.to_csv(os.path.join(directory, "geo_data.csv"), index=False)
    return None


def get_location(location, key):
    """Retrieve the geographic information for a specified location.

    Parameters
    ----------
    location: str
        location for which the information is to be retrieved
    key: str
        private key of a required Positionstack account

    Returns
    -------
    results: pandas.DataFrame
        contains various geographic information if the request was successful
    """
    url = f"http://api.positionstack.com/v1/forward?access_key={key}&query={location}&limit=1&country=DE"
    try:
        results = pd.DataFrame(requests.get(url).json()["data"])
    except KeyError:
        return None
    else:
        results["location"] = [location]
        return results


if __name__ == "__main__":
    # if the script is executed directly, the directory must be passed via the command line
    dir_ = parse_directory()
    main(dir_)
