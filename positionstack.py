import pandas as pd
from tqdm import tqdm
import requests

import config

api_key = config.positionstack_key
df = pd.read_csv("cleaned_long.csv")
geo_data = pd.DataFrame()
locations = df["location_y"].unique()
for location in tqdm(locations):
    url = f"http://api.positionstack.com/v1/forward?access_key={api_key}&query={location}&limit=1&country=DE"
    try:
        data = pd.DataFrame(requests.get(url).json()["data"])
    except:
        data = pd.DataFrame(columns=geo_data.columns)
    data["location"] = [location]
    geo_data = pd.concat([geo_data, data], ignore_index=True)

geo_data.to_csv("data2/geo_data2.csv")