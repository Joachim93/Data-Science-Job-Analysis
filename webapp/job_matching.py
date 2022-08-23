import streamlit as st
import pandas as pd


def job_matching(df):
    st.title("Job Matching")

    with st.form(key="inputs"):
        experience = st.radio("how much professional experience do you have?", ["little", "some", "much"])
        st.write("job with lower experience levels will always be included")
        education = st.radio("what level of education do you have?", ["no degree", "bachelor", "master", "phd"])
        st.write("job with lower education levels will always be included")

        languages = st.multiselect("languages", df["Languages"].columns)
        technologies = st.multiselect("technologies", df["Technologies"].columns)
        libraries = st.multiselect("python libraries", df["Libraries"].columns)

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

        query = languages + technologies + libraries

        df_query = df_filtered.droplevel(0, axis=1).loc[:, query]

        matches = df_query.sum(axis=1)
        matches.name = "matches"
        df_display = pd.concat([matches, df_query, df_filtered["General_info"][["link", "title", "company"]]], axis=1).sort_values("matches", ascending=False)

        df_display = df_display.loc[df_display["matches"] >= min_matches]

        st.write(f"{df_display.shape[0]} job openings are fitting your criteria")
        st.dataframe(df_display)
