import streamlit as st
import pandas as pd

from region_analysis import region_analysis
from requirement_analysis import requirements_analysis
from job_matching import job_matching


def main():
    st.set_page_config(layout="wide")
    data_long, data_requirements = load_data()

    st.sidebar.write("Sidebar")
    options = st.sidebar.radio("Pages", options=["Home", "Requirements Analysis", "Region Analysis", "Job Matching"])
    if options == "Requirements Analysis":
        requirements_analysis(data_requirements)
    elif options == "Region Analysis":
        region_analysis(data_long)
    elif options == "Job Matching":
        job_matching(data_requirements)
    else:
        st.write("TODO")


@st.cache
def load_data():
    df_long = pd.read_csv("data2/cleaned_long_geo.csv")
    # geo_data = pd.read_csv("data2/geo_data.csv", index_col=0)
    # df_filtered = df_long.loc[(df_long["latitude"].notnull()) & (df_long["confidence"] == 1)
    #                           & (df_long["title_cat"] != "Others")]
    df_requirements = pd.read_csv("data2/cleaned_wide.csv")
    groups = 21*["General_info"] + 18*["Languages"] + 19*["Technologies"] + 14*["Libraries"] + 4*["Education"] \
             + 5*["Degree"] + 8*["Knowledge"] + 10*["Soft Skills"] + 4*["Experience"]
    df_requirements.columns = pd.MultiIndex.from_arrays([groups, df_requirements.columns])
    # df_requirements = pd.read_csv("../data2/requirements.csv")
    return df_long, df_requirements


if __name__ == "__main__":
    main()
