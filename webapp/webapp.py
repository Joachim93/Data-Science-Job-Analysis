import streamlit as st
import pandas as pd

from region_analysis import region_analysis
from requirement_analysis import requirements_analysis
from job_matching import job_matching


def main():
    st.set_page_config(layout="wide")
    data_long, data_requirements = load_data()

    # st.sidebar.write("Sidebar")
    options = st.sidebar.radio("Pages", options=["Requirements Analysis", "Region Analysis", "Job Matching"])
    if options == "Requirements Analysis":
        requirements_analysis(data_requirements)
    elif options == "Region Analysis":
        region_analysis(data_long)
    else:
        job_matching(data_requirements)


@st.cache
def load_data():
    df_long = pd.read_csv("data2/cleaned_long_geo.csv")
    df_long = df_long.loc[df_long["title_category"] != "Others"]
    df_wide = pd.read_csv("data2/cleaned_wide.csv")
    groups = 21*["General_info"] + 18*["Languages"] + 19*["Technologies"] + 14*["Libraries"] + 4*["Education"] \
             + 5*["Degree"] + 8*["Knowledge"] + 10*["Soft Skills"] + 4*["Experience"]
    df_wide.columns = pd.MultiIndex.from_arrays([groups, df_wide.columns])
    return df_long, df_wide


if __name__ == "__main__":
    main()
