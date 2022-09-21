"""
Script to generate the webapp.
"""

import streamlit as st
import pandas as pd

from geographical_analysis import geographical_analysis
from requirement_analysis import requirements_analysis
from job_matching import job_matching


def main():
    """Loads the data and implements the functionality of the sidebar."""

    st.set_page_config(layout="wide")
    data_long, data_wide = load_data()
    options = st.sidebar.radio("Pages", options=["Requirements Analysis", "Geographical Analysis", "Job Matching"])
    if options == "Requirements Analysis":
        requirements_analysis(data_wide)
    elif options == "Geographical Analysis":
        geographical_analysis(data_long)
    else:
        job_matching(data_wide)


@st.cache
def load_data():
    """Loading the required data for the webapp.

    Another column index is added to the long format data to make it easier to group the different requirements.

    Returns
    -------
    df_long: pandas.DataFrame
        contains one entry per location
    df_wide: pandas.DataFrame
        contains one entry per job
    """

    df_long = pd.read_csv("data/data_long.csv")
    df_long = df_long.loc[df_long["title_category"] != "Others"]
    df_wide = pd.read_csv("data/data_wide.csv")
    df_wide = df_wide.loc[df_wide["title_category"] != "Others"]
    if "main_region" in df_wide.columns:
        groups = 21 * ["General_info"] + 18 * ["Languages"] + 19 * ["Tools"] + 14 * ["Libraries"] + 4 * ["Education"] \
                 + 5 * ["Degree"] + 8 * ["Knowledge"] + 10 * ["Soft Skills"] + 4 * ["Experience"]
    else:
        groups = 20 * ["General_info"] + 18 * ["Languages"] + 19 * ["Tools"] + 14 * ["Libraries"] + 4 * ["Education"] \
                 + 5 * ["Degree"] + 8 * ["Knowledge"] + 10 * ["Soft Skills"] + 4 * ["Experience"]
    df_wide.columns = pd.MultiIndex.from_arrays([groups, df_wide.columns])
    return df_long, df_wide


if __name__ == "__main__":
    main()
