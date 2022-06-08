import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Distribution of Data Science Jobs in Germany")

df_long = pd.read_csv("data2/cleaned_long.csv")
geo_data = pd.read_csv("data2/geo_data.csv", index_col=0)
df_filtered = df_long.loc[(df_long["latitude"].notnull()) & (df_long["confidence"] == 1)
                          & (df_long["title_cat"] != "Others")]

col1, col2 = st.columns([1,3])

st.sidebar.write("Sidebar")

with col1:
    choices = st.multiselect(label="Select job titles you're interested in",
                                     options=df_filtered["title_cat"].unique(),
                                     default=df_filtered["title_cat"].unique())

df_choice = df_filtered.loc[df_long["title_cat"].isin(choices)]
counts = df_choice.groupby("location_y")["link"].count().reset_index().rename({"location_y": "location", "link": "count"}, axis=1)


# gruppierte Werte plotten
df_map = pd.merge(counts, geo_data[["location", "latitude", "longitude"]], on="location", how="left")
df_map["size"] = np.log(df_map["count"])

fig = px.scatter_mapbox(df_map,
                        lat="latitude", lon="longitude",
                        # color="link",
                        hover_name="location",
                        hover_data=["count"],
                        color_discrete_sequence=["blue"],
                        mapbox_style="carto-positron",
                        size="size",
                        size_max=20,
                        zoom=5,
                        center={"lat": 51, "lon": 10},
                        width=600, height=800)
with col2:
    st.plotly_chart(fig)
