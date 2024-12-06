"""
This script contains the function for job matching of the webapp.
"""

import pandas as pd
import streamlit as st


def job_matching(df):
    """Realizes the job matching of the webapp.

    Filters the data first by the specified degree and work experience. Creates a ranking of all remaining jobs, which
    ranks them according to their similarity to the applicant's stated skills.

    Parameters
    ----------
    df: pandas.DatFrame
        wide format data (contains one entry per job)
    """

    st.title("Job Matching")
    st.write("This interface provides a ranking of all jobs contained in the database ordered by their similarity to"
             " the specified skills.")
    with st.form(key="inputs"):
        col1, col2 = st.columns(2)
        with col1:
            experience = st.radio("how much professional experience do you have?", ["little (0-2 years)",
                                                                                    "some (3-4 years)",
                                                                                    "much (5+ years)"])
        with col2:
            education = st.radio("what level of education do you have?", ["no degree", "bachelor", "master", "phd"])

        col1, col2, col3 = st.columns(3)
        with col1:
            languages = st.multiselect("languages", df["Languages"].columns)
            tools = st.multiselect("tools", df["Tools"].columns)
        with col2:
            libraries = st.multiselect("python libraries", df["Libraries"].columns)
            knowledge = st.multiselect("knowledge", df["Knowledge"].columns)
        with col3:
            soft_skills = st.multiselect("soft_skills", df["Soft Skills"].columns)
            min_matches = st.number_input("minimum number of matches to be displayed", min_value=1)

        submitted = st.form_submit_button("Search Jobs")

    if submitted:
        if experience == "little (0-2 years)":
            df_filtered = df.loc[df["Experience", "no_experience_information"] | df["Experience", "little_experience"]]
        elif experience == "some (3-4 years)":
            df_filtered = df.loc[
                df["Experience", "no_experience_information"] | df["Experience", "little_experience"] | df[
                    "Experience", "some_experience"]]
        else:
            df_filtered = df
        if education == "no degree":
            df_filtered = df_filtered.loc[df_filtered["Education", "no_degree_info"]]
        elif education == "bachelor":
            df_filtered = df_filtered.loc[df_filtered["Education", "no_degree_info"] | df_filtered["Education", "bachelor"]]
        elif education == "master":
            df_filtered = df_filtered.loc[df_filtered["Education", "no_degree_info"] | df_filtered["Education", "master"]]

        query = languages + tools + libraries + knowledge + soft_skills

        df_query = df_filtered.droplevel(0, axis=1).loc[:, query]

        matches = df_query.sum(axis=1)
        matches.name = "matches"
        df_display = pd.concat([matches, df_query, df_filtered["General_info"][["link", "title", "company"]]], axis=1).sort_values("matches", ascending=False)

        df_display = df_display.loc[df_display["matches"] >= min_matches]

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
