import pandas as pd
from tqdm import tqdm
import requests
import concurrent.futures

import config


def main(df):
    print("get geo data")
    api_key = config.positionstack_key
    locations = df["location"].unique()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        geo_data = list(tqdm(executor.map(lambda x: get_location(x, api_key), locations), total=len(locations)))
    geo_data = pd.concat(geo_data)
    geo_data.to_csv("data/geo_data.csv", index=False)
    return None


def get_location(location, key):
    url = f"http://api.positionstack.com/v1/forward?access_key={key}&query={location}&limit=1&country=DE"
    try:
        results = pd.DataFrame(requests.get(url).json()["data"])
    except KeyError:
        pass
    else:
        results["location"] = [location]
        return results
    return None


if __name__ == "__main__":
    data = pd.read_csv("data2/cleaned_long2.csv")
    main(data)
