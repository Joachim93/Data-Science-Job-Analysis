import streamlit as st
import plotly.express as px
import numpy as np


def region_analysis(df_long):
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
        df_choice = df_long.loc[df_long["title_category"].isin(choices_selected)]
        # counts = df_choice.groupby("location_y")["link"].count().reset_index().rename(
        #     {"location_y": "location", "link": "count"}, axis=1)

        # df_map = pd.merge(counts, geo_data[["location", "latitude", "longitude"]], on="location", how="left")

        df_map = df_choice.groupby(["location", "latitude", "longitude"], as_index=False)["link"].agg({"count": "count"})

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