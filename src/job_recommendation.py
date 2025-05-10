"""
This script contains the function for job matching of the web app.
"""

import pandas as pd
import streamlit as st


def job_recommendation(df):
    """Realizes the job matching of the web app.

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
            experience = st.selectbox("Years of Professional Experience", ["Little (<=2 years)",
                                                                    "Some (3-4 years)",
                                                                    "Much (>=5 years)"])
            languages = st.multiselect("Programming Languages", df["Languages"].columns.str.replace("_", " ").str.title())
            databases = st.multiselect("Databases", df["Databases"].columns.str.replace("_", " ").str.title())
            knowledge = st.multiselect("Machine Learning Knowledge", df["Knowledge"].columns.str.replace("_", " ").str.title())
            company_size = st.selectbox("Company Size", ["All", "Small (0-1,000)", "Medium (1,001-10,000)", "Big (>10,000)"])
        with col2:
            education = st.selectbox("Level of Education", ["No Degree", "Bachelor", "Master", "Phd"])
            tools = st.multiselect("Tools", df["Tools"].columns.str.replace("_", " ").str.title())
            libraries = st.multiselect("Python Libraries", df["Libraries"].columns.str.replace("_", " ").str.title())
            soft_skills = st.multiselect("Soft Skills", df["Soft_skills"].columns.str.replace("_", " ").str.title())
            min_matches = st.number_input("Minimum Number of Matches to be Displayed", min_value=1)

        submitted = st.form_submit_button("Search Jobs")

    if submitted:
        # when filtering for experience, jobs with less required experience are also included (same goes for degree)
        if experience == "Little (<=2 years)":
            df = df.loc[df["Experience", "no_experience_information"] | df["Experience", "<=2_years_experience"]]
        elif experience == "Some (3-4 years)":
            df = df.loc[df["Experience", "no_experience_information"] | df["Experience", "<=2_years_experience"] | 
                        df["Experience", "3-4_years_experience"]]
        
        if education == "No Degree":
            df = df.loc[df["Degree", "no_degree_info"]]
        elif education == "Bachelor":
            df = df.loc[df["Degree", "no_degree_info"] | df["Degree", "bachelor"]]
        elif education == "Master":
            df = df.loc[df["Degree", "no_degree_info"] | df["Degree", "master"]]

        size_groups = {
            "10,001+": "Big (>10,000)", 
            "5001-10,000": "Medium (1,001-10,000)", 
            "2501-5000": "Medium (1,001-10,000)", 
            "1001-2500": "Medium (1,001-10,000)",
            "501-1000": "Small (0-1,000)", 
            "251-500": "Small (0-1,000)", 
            "51-250": "Small (0-1,000)", 
            "0-50": "Small (0-1,000)"
        }
        if company_size != "All":
            df = df.loc[df["General_info", "company_size"].map(size_groups) == company_size]

        query = languages + tools + databases + libraries + knowledge + soft_skills
        query = [element.replace(' ', '_').lower() for element in query]

        df_query = df.droplevel(0, axis=1).loc[:, query]

        matches = df_query.sum(axis=1)
        matches.name = "matches"
        df_display = pd.concat([matches, df_query, df["General_info"][["title", "company", "link"]]], axis=1).sort_values("matches", ascending=False)
        
        df_display = df_display.loc[df_display["matches"] >= min_matches].reset_index(drop=True)
        df_display.columns = df_display.columns.str.replace("_", " ").str.title()

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
