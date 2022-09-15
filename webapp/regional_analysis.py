"""
This script contains the function for regional analysis of the webapp.
"""

import streamlit as st
import plotly.express as px
import numpy as np


def regional_analysis(df):
    """Realizes the regional analysis of the webapp.

    Filters the data by the specified job titles and displays the distribution of jobs in Germany on a scatter map.

    Parameters
    ----------
    df: pandas.DatFrame
        long format data (contains one entry per location)
    """

    st.title("Distribution of Data Science Jobs in Germany")
    col1, col2 = st.columns([1, 2])
    choices = ["Data Scientist", "Data Analyst", "Data Engineer", "Machine Learning Engineer", "Software Engineer",
               "Data Science Consultant", "Data Science Manager"]

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
        check_m = st.checkbox("Data Science Manager", value=True)

        selected = [check_ds, check_da, check_de, check_mle, check_se, check_dsc, check_m]
        choices_selected = [choice for (choice, value) in zip(choices, selected) if value]
        df_choice = df.loc[df["title_category"].isin(choices_selected)]

        df_map = df_choice.groupby(["location", "latitude", "longitude"], as_index=False)["link"].agg({"number of jobs": "count"})

        df_map["size"] = np.log(df_map["number of jobs"] + 1)

        fig = px.scatter_mapbox(df_map,
                                lat="latitude", lon="longitude",
                                hover_name="location",
                                hover_data={"latitude": False, "longitude": False, "size": False,
                                            "number of jobs": True},
                                color_discrete_sequence=["blue"],
                                mapbox_style="carto-positron",
                                size="size",
                                size_max=20,
                                zoom=5,
                                opacity=0.5,
                                center={"lat": 51, "lon": 10},
                                width=650, height=750)

        with col2:
            st.plotly_chart(fig)
