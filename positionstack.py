import pandas as pd
from tqdm import tqdm
import requests
import concurrent.futures

import config


def get_location(location):
    api_key = config.positionstack_key
    url = f"http://api.positionstack.com/v1/forward?access_key={api_key}&query={location}&limit=1&country=DE"
    try:
        results = pd.DataFrame(requests.get(url).json()["data"])
        results["location"] = [location]
    except:
        pass
    return results


df = pd.read_csv("data2/cleaned_long2.csv")
locations = df["location"].unique()

with concurrent.futures.ThreadPoolExecutor() as executor:
    geo_data = list(tqdm(executor.map(get_location, locations), total=len(locations)))

geo_data = pd.concat(geo_data)

geo_data.to_csv("data2/geo_data2.csv", index=False)
