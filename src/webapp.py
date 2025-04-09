"""
Script to generate the webapp.
"""

import joblib

import pandas as pd
import streamlit as st

from geographical_analysis import geographical_analysis
from job_recommendation import job_recommendation
from salary_estimation import salary_estimation
from requirement_analysis import requirements_analysis

# st.set_page_config(layout="wide")

def main():
    """Loads the data and implements the functionality of the sidebar."""

    data_long, data_wide = load_data()
    model = load_model()
    st.sidebar.title("Analyzing the Data Science Job Market in Germany")
    st.sidebar.write("")
    st.sidebar.write("")
    options = st.sidebar.selectbox("Pages", options=["Requirements Analysis", "Geographical Analysis", 
                                                 "Salary Estimation", "Job Recommendation"])
    st.sidebar.write("")
    st.sidebar.write("")

    if options == "Requirements Analysis":
        requirements_analysis(data_wide)
    elif options == "Geographical Analysis":
        geographical_analysis(data_long)
    elif options == "Salary Estimation":
        salary_estimation(model)
    else:
        job_recommendation(data_wide)


@st.cache_data
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
        groups = (21*["General_info"] + 18*["Languages"] + 31*["Tools"] + 21*["Databases"] + 18*["Libraries"] 
                  + 4*["Degree"] + 5*["Major"] + 13*["Knowledge"] + 10*["Soft_skills"] + 4*["Experience"])
    else:
        groups = (20*["General_info"] + 18*["Languages"] + 31*["Tools"] + 21*["Databases"] + 18*["Libraries"] 
                  + 4*["Degree"] + 5*["Major"] + 13*["Knowledge"] + 10*["Soft_skills"] + 4*["Experience"])
    df_wide.columns = pd.MultiIndex.from_arrays([groups, df_wide.columns])
    return df_long, df_wide


@st.cache_data
def load_model():
    """Loads the model for the prediction of the salary.

    Returns
    -------
    model: sklearn.pipeline.Pipeline
        model for the prediction of the salary
    """

    model = joblib.load("models/model.joblib")
    return model


if __name__ == "__main__":
    main()
