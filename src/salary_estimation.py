import pandas as pd
import streamlit as st

from webscraper import scrape_features
from preprocessing import preprocess_data

def salary_estimation(model):
    st.header("Salary Estimation for Data Science Jobs")
    st.sidebar.write("This interface offers the possibility to estimate the salary for a given job ad on Stepstone.")
    st.write("")
    
    # Eingabeformular für die Texteingabe
    with st.form(key='salary_estimation_form'):
        job_ad = st.text_input("Job Ad", placeholder="Enter the link to the job ad on Stepstone")
        
        # Submit-Button
        submit_button = st.form_submit_button(label='Estimate Salary')
    
    # Wenn der Submit-Button geklickt wird
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
        label_width = 20  # Adjust this value to change alignment
        st.markdown(f"""
        ```
        {'Job Title:':<{label_width}} {results["Job Title"]}
        {'Company:':<{label_width}} {results["Company"]}
        {'Location:':<{label_width}} {results["Location"]}
        {'Estimated Salary:':<{label_width}} {results["Salary"]:} €
        ```
        """)    