"""
This script contains the function for job matching of the webapp.
"""

import streamlit as st
import pandas as pd


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
    with st.form(key="inputs"):
        col1, col2 = st.columns(2)
        with col1:
            experience = st.radio("how much professional experience do you have?", ["little", "some", "much"])
            st.write("job with lower experience levels will always be included")
        with col2:
            education = st.radio("what level of education do you have?", ["no degree", "bachelor", "master", "phd"])
            st.write("job with lower education levels will always be included")

        col1, col2, col3 = st.columns(3)
        with col1:
            languages = st.multiselect("languages", df["Languages"].columns)
            tools = st.multiselect("tools", df["Tools"].columns)
        with col2:
            libraries = st.multiselect("python libraries", df["Libraries"].columns)
            knowledge = st.multiselect("knowledge", df["Knowledge"].columns)
        with col3:
            soft_skills = st.multiselect("soft_skills", df["Soft Skills"].columns)
            min_matches = st.number_input("Select the minimum number of matches for an opening to be displayed", min_value=0)

        submitted = st.form_submit_button("Search Jobs")

    if submitted:
        if experience == "little":
            df_filtered = df.loc[df["Experience", "no_experience_information"] | df["Experience", "little_experience"]]
        elif experience == "some":
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

        st.write(f"{df_display.shape[0]} job openings are fitting your criteria")
        st.dataframe(df_display)
