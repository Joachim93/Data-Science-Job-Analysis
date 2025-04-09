"""
This script contains the function for job matching of the webapp.
"""

import pandas as pd
import streamlit as st


def job_recommendation(df):
    """Realizes the job matching of the webapp.

    Filters the data first by the specified degree and work experience. Creates a ranking of all remaining jobs, which
    ranks them according to their similarity to the applicant's stated skills.

    Parameters
    ----------
    df: pandas.DatFrame
        wide format data (contains one entry per job)
    """

    st.header("Job Recommender System")
    st.sidebar.write("This interface provides a recommendation system for job openings based on the user's skills and preferences.")
    st.write("")       
    with st.form(key="inputs"):
        col1, col2 = st.columns(2)
        with col1:
            experience = st.selectbox("Years of professional experience", ["little (<=2 years)",
                                                                    "some (3-4 years)",
                                                                    "much (>=5 years)"])
            languages = st.multiselect("Programming languages", df["Languages"].columns)
            databases = st.multiselect("Databases", df["Databases"].columns)
            knowledge = st.multiselect("Machine Learning Knowledge", df["Knowledge"].columns)
            company_size = st.selectbox("Company size", ["All", "small (0-1,000)", "medium (1,001-10,000)", "big (>10,000)"])
        with col2:
            education = st.selectbox("Level of education", ["no degree", "bachelor", "master", "phd"])
            tools = st.multiselect("Tools", df["Tools"].columns)
            libraries = st.multiselect("Python libraries", df["Libraries"].columns)
            soft_skills = st.multiselect("Soft skills", df["Soft_skills"].columns)
            min_matches = st.number_input("Minimum number of matches to be displayed", min_value=1)  # Fixed indentation

        submitted = st.form_submit_button("Search Jobs")

    if submitted:
        # when filtering for experience, jobs with less required experience are also included
        if experience == "little (<=2 years)":
            df = df.loc[df["Experience", "no_experience_information"] | df["Experience", "<=2_years_experience"]]
        elif experience == "some (3-4 years)":
            df = df.loc[df["Experience", "no_experience_information"] | df["Experience", "<=2_years_experience"] | 
                        df["Experience", "3-4_years_experience"]]
        
        if education == "no degree":
            df = df.loc[df["Degree", "no_degree_info"]]
        elif education == "bachelor":
            df = df.loc[df["Degree", "no_degree_info"] | df["Degree", "bachelor"]]
        elif education == "master":
            df = df.loc[df["Degree", "no_degree_info"] | df["Degree", "master"]]

        size_groups = {
            "10,001+": "big (>10,000)", 
            "5001-10,000": "medium (1,001-10,000)", 
            "2501-5000": "medium (1,001-10,000)", 
            "1001-2500": "medium (1,001-10,000)",
            "501-1000": "small (0-1,000)", 
            "251-500": "small (0-1,000)", 
            "51-250": "small (0-1,000)", 
            "0-50": "small (0-1,000)"
        }
        if company_size != "All":
            df = df.loc[df["General_info", "company_size"].map(size_groups) == company_size]

        query = languages + tools + databases + libraries + knowledge + soft_skills

        df_query = df.droplevel(0, axis=1).loc[:, query]

        matches = df_query.sum(axis=1)
        matches.name = "matches"
        df_display = pd.concat([matches, df_query, df["General_info"][["title", "company", "link"]]], axis=1).sort_values("matches", ascending=False)

        df_display = df_display.loc[df_display["matches"] >= min_matches].reset_index(drop=True)

        num_jobs = df_display.shape[0]
        st.write(f"{num_jobs} job openings are fitting the criteria")

        if num_jobs:
            st.dataframe(df_display)
            st.download_button(
                label="Download",
                data=df_display.to_csv(),
                file_name='best_jobs.csv',
                mime='text/csv',
            )
