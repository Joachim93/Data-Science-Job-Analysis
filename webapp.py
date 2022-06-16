import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

@st.cache
def load_data():
    df_long = pd.read_csv("data2/cleaned_long.csv")
    geo_data = pd.read_csv("data2/geo_data.csv", index_col=0)
    df_filtered = df_long.loc[(df_long["latitude"].notnull()) & (df_long["confidence"] == 1)
                              & (df_long["title_cat"] != "Others")]
    df_requirements = pd.read_csv("data2/skills.csv").drop(["link", "content"], axis=1)
    return df_filtered, geo_data, df_requirements

def region_analysis(df_filtered, geo_data):
    st.title("Distribution of Data Science Jobs in Germany")
    col1, col2 = st.columns([1, 2])
    choices = ["Data Scientist", "Data Analyst", "Data Engineer", "Machine Learning Engineer", "Software Engineer",
               "Data Science Consultant", "Manager"]

    with col1:
        st.title("")
        st.markdown("#### Please select the jobs you're interested in.")
        st.title("")

        check_ds = st.checkbox("Data Scientist", value=True)
        check_da = st.checkbox("Data Analyst", value=True)
        check_de = st.checkbox("Data Engineer", value=True)
        check_mle = st.checkbox("Machine Learning Engineer", value=True)
        check_se = st.checkbox("Software Engineer", value=True)
        check_dsc = st.checkbox("Data Science Consultant", value=True)
        check_m = st.checkbox("Manager", value=True)

        selected = [check_ds, check_da, check_de, check_mle, check_se, check_dsc, check_m]
        choices_selected = [choice for (choice, value) in zip(choices, selected) if value]
        df_choice = df_filtered.loc[df_filtered["title_cat"].isin(choices_selected)]
        counts = df_choice.groupby("location_y")["link"].count().reset_index().rename(
            {"location_y": "location", "link": "count"}, axis=1)

        df_map = pd.merge(counts, geo_data[["location", "latitude", "longitude"]], on="location", how="left")
        df_map["size"] = np.log(df_map["count"] + 1)

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

def requirements_analysis(df_requirements):
    st.title("Distribution of Requirements for Data Science Jobs in Germany")
    col1, col2 = st.columns([1, 2])
    choices = ["Data Scientist", "Data Analyst", "Data Engineer", "Machine Learning Engineer", "Software Engineer",
               "Data Science Consultant", "Manager"]

    with col1:
        st.title("")
        st.markdown("#### Please select the jobs you're interested in.")
        st.title("")

        # check_ds = st.checkbox("Data Scientist", value=True)
        # check_da = st.checkbox("Data Analyst", value=True)
        # check_de = st.checkbox("Data Engineer", value=True)
        # check_mle = st.checkbox("Machine Learning Engineer", value=True)
        # check_se = st.checkbox("Software Engineer", value=True)
        # check_dsc = st.checkbox("Data Science Consultant", value=True)
        # check_m = st.checkbox("Manager", value=True)

        choice = st.radio("Pages", options=choices)

    df_requirements = df_requirements.loc[df_requirements["title_cat"] == choice]
    percentages = (df_requirements.drop("title_cat", axis=1).sum().sort_values(ascending=False) * 100 / len(df_requirements)).apply(lambda x: round(x,2))
    fig = px.bar(percentages[:20], title="Most required Skills for Data Science Jobs",
                 labels={"value": "Percentages", "index": "Skills"})
    fig.layout.update(showlegend=False)
    with col2:
        st.plotly_chart(fig)

df_filtered, geo_data, df_requirements = load_data()

st.sidebar.write("Sidebar")
options = st.sidebar.radio("Pages", options=["Home", "Requirements Analysis", "Region Analysis"])
if options == "Requirements Analysis":
    requirements_analysis(df_requirements)
if options == "Region Analysis":
    region_analysis(df_filtered, geo_data)
else:
    st.write("TODO")






