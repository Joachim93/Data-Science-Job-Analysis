import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

@st.cache
def load_data():
    df_long = pd.read_csv("data2/cleaned_long_geo.csv")
    # geo_data = pd.read_csv("data2/geo_data.csv", index_col=0)
    # df_filtered = df_long.loc[(df_long["latitude"].notnull()) & (df_long["confidence"] == 1)
    #                           & (df_long["title_cat"] != "Others")]
    df_requirements = pd.read_csv("data2/requirements.csv").drop(["link", "content"], axis=1)
    return df_long, df_requirements

def region_analysis(df_long):
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

def requirements_analysis(df_requirements):
    st.title("Requirements for Data Science Jobs in Germany")
    col1, col2, col3 = st.columns(3)
    choices = ["All", "Data Scientist", "Data Analyst", "Data Engineer", "Machine Learning Engineer", "Software Engineer",
               "Data Science Consultant", "Manager"]

    with col1:
        selected_skills = st.selectbox("Which Skills are you interested in?",
                                       ("All", "Languages", "Technologies", "Libraries", "Education", "Degree", "Experience"))

    with col2:
        first_choice = st.selectbox("Which Jobtitle are you interested in?", choices)

    choices_new = [choice for choice in choices if choice != first_choice]

    with col3:
        second_choice = st.selectbox("Choose a second Jobtitle (optional)", ["None"] + choices_new)

    if second_choice == "None":
        choices_selected = [first_choice]
    else:
        choices_selected = [first_choice, second_choice]

    if first_choice != "All":
        df_first = df_requirements.loc[df_requirements["title_cat"] == first_choice]
    else:
        df_first = df_requirements
    percentages_first = pd.Series(
        df_first.drop("title_cat", axis=1).sum() * 100 / len(df_first),
        name=first_choice).to_frame()
    percentages_first["type"] = 19 * ["Languages"] + 20 * ["Technologies"] + 14 * ["Libraries"] + 3 * ["Education"] + \
                                5 * ["Degree"] + 3 * ["Experience"]

    if second_choice == "None":
        percentages = percentages_first
    else:
        if second_choice != "All":
            df_second = df_requirements.loc[df_requirements["title_cat"] == second_choice]
        else:
            df_second = df_requirements
        percentages_second = pd.Series(
            df_second.drop("title_cat", axis=1).sum() * 100 / len(df_second),
            name=second_choice).to_frame()
        percentages = pd.merge(percentages_first, percentages_second, left_index=True, right_index=True)

    percentages = percentages.reset_index()
    percentages[first_choice] = percentages[first_choice].apply(lambda x: round(x, 2))
    if second_choice != "None":
        percentages = percentages.loc[(percentages[first_choice] > 0) | (percentages[second_choice] > 0)]
        percentages[second_choice] = percentages[second_choice].apply(lambda x: round(x, 2))
    else:
        percentages = percentages.loc[percentages[first_choice] > 0]
    percentages = percentages.sort_values(choices_selected, ascending=False)

    if selected_skills != "All":
        percentages = percentages.loc[percentages["type"] == selected_skills]

    fig = px.bar(percentages,
                 x="index",
                 y=choices_selected,
                 # title="Most required Skills for Data Science Jobs",
                 labels={"value": "Percentages"},
                 barmode="group",
                 width=1050, height=500)
    fig.update_layout(legend={"yanchor":"top", "y": 0.99, "xanchor": "right", "x": 0.99})
    st.plotly_chart(fig)


data_long, data_requirements = load_data()

st.sidebar.write("Sidebar")
options = st.sidebar.radio("Pages", options=["Home", "Requirements Analysis", "Region Analysis"])
if options == "Requirements Analysis":
    requirements_analysis(data_requirements)
elif options == "Region Analysis":
    region_analysis(data_long)
else:
    st.write("TODO")






