"""
This script contains the function for the salary estimation of the webapp.
"""

import streamlit as st

from webscraper import scrape_features
from preprocessing import preprocess_data


def salary_estimation(model):
    """Realizes the salary estimation of the webapp.

    Scrapes the data of a specified job advertisement on “https://www.stepstone.de”, processes and transforms it
    and then estimates the salary of the job advertisement obased on the available information.

    Parameters
    ----------
    model: sklearn.pipeline.Pipeline
        trained model used to estimate the salary
    """

    st.header("Salary Estimation for Data Science Jobs")
    st.sidebar.write("This interface offers the possibility to estimate the salary for a given job ad on Stepstone.")
    st.sidebar.write("**Note**: The functionality of this module depends on an external website that is updated regularly. " \
    "Therefore, it cannot be guaranteed that this module will continue to function properly after future changes to the website.")
    st.write("")

    with st.form(key='salary_estimation_form'):
        job_ad = st.text_input("Job Ad", placeholder="Enter the link to the job ad on Stepstone")
        submit_button = st.form_submit_button(label='Estimate Salary')
    
    if submit_button:
        data = scrape_features(job_ad)
        data = preprocess_data(data)
        features = model["imputer"].feature_names_in_
        salary = model.predict(data[features])[0]

        results = {}
        results["Job Title"] = data["title"].iloc[0]
        results["Company"] = data["company"].iloc[0]
        results["Location"] = data["main_location"].iloc[0]
        results["Salary"] = round(salary)
    
        st.write("")
        label_width = 20
        st.markdown(f"""
        ```
        {'Job Title:':<{label_width}} {results["Job Title"]}
        {'Company:':<{label_width}} {results["Company"]}
        {'Location:':<{label_width}} {results["Location"]}
        {'Estimated Salary:':<{label_width}} {results["Salary"]:} €
        ```
        """)    
