"""
This script contains the function for geographical analysis of the web app.
"""

import numpy as np
import streamlit as st
import plotly.express as px


def geographical_analysis(df):
    """Realizes the geographical analysis of the web app.

    Filters the data by the specified job titles and displays the distribution of jobs in Germany on a scatter map.

    Parameters
    ----------
    df: pandas.DatFrame
        long format data (contains one entry per location)
    """

    st.header("Regional Distribution of Data Science Jobs")
    st.sidebar.write("This interface provides an overview of the geographical distribution of available data science jobs in Germany."
            " The data can be filtered by job title.")
    st.write("")   

    if "latitude" in df.columns:
        options = ["Data Scientist", "Data Analyst", "Data Engineer", "Machine Learning Engineer", "Software Engineer",
                   "Data Science Consultant", "Data Science Manager"]

        col1, col2, col3 = st.columns(3)
        with col1:
            check_ds = st.checkbox("Data Scientist", value=True)
            check_da = st.checkbox("Data Analyst", value=True)
            check_de = st.checkbox("Data Engineer", value=True)
        with col2:
            check_mle = st.checkbox("Machine Learning Engineer", value=True)
            check_se = st.checkbox("Software Engineer", value=True)
        with col3:
            check_dsc = st.checkbox("Data Science Consultant", value=True)
            check_m = st.checkbox("Data Science Manager", value=True)


        selection = [check_ds, check_da, check_de, check_mle, check_se, check_dsc, check_m]
        choices_selected = [choice for (choice, value) in zip(options, selection) if value]
        df_choice = df.loc[df["title_category"].isin(choices_selected)]

        df_map = df_choice.groupby(["location", "latitude", "longitude"], as_index=False)["link"].agg({"number of jobs": "count"})

        df_map["size"] = np.log(df_map["number of jobs"] + 1)

        fig = px.scatter_mapbox(df_map,
                                lat="latitude", lon="longitude",
                                hover_name="location",
                                hover_data={"latitude": False, "longitude": False, "size": False,
                                            "number of jobs": True},
                                color_discrete_sequence=["blue"],
                                mapbox_style="open-street-map",
                                size="size",
                                size_max=20,
                                zoom=5,
                                opacity=0.5,
                                center={"lat": 51, "lon": 10},
                                width=500, height=750)

        col1, col2, col3 = st.columns([1, 8, 2])
        with col2:
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.write("The data you provided does not contain geographic information, which is required for this visualization.")
