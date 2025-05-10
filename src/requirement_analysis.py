"""
This script contains the function for requirement analysis of the web app.
"""

import pandas as pd
import streamlit as st
import plotly.express as px


def requirements_analysis(df):
    """Realizes the requirement analysis of the web app.

    Filters the data according to the specified information and calculates for each of the specified attributes the
    percentage of jobs where this attribute occurs.

    Parameters
    ----------
    df: pandas.DatFrame
        wide format data (contains one entry per job)
    """

    st.header("Top Requirements for Data Science Jobs")
    st.sidebar.write("This interface offers the possibility to display the most important requirements for different job"
             " titles, experience levels and company sizes.")
    st.write("")
    col1, col2 = st.columns(2)
    choices_jobtitle = ["All"] + list(df["General_info", "title_category"].unique())
    choices_requirement = ["All"] + list(df.columns.unique(0).drop(["General_info", "Major", "Degree", "Experience"]))
    choices_experience = ["All", "<=2 Years Experience", "3-4 Years Experience", ">=5 Years Experience"]
    choices_size = ["All", "Small (0-1,000)", "Medium (1,001-10,000)", "Big (>10,000)"]

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

    with col1:
        selected_requirements = st.selectbox("Which Requirements are you interested in?", choices_requirement)
        selected_experience = st.selectbox("Which experience level are you interested in?", choices_experience)

    with col2:
        selected_jobtitle = st.selectbox("Which jobtitle are you interested in?", choices_jobtitle)
        selected_size = st.selectbox("Which company size are you interested in?", choices_size)

    if selected_requirements != "All":
        columns = selected_requirements
    else:
        columns = df.columns.unique(0).drop(["General_info", "Major", "Degree", "Experience"])
    if selected_experience != "All":
        df = df.loc[df["Experience", selected_experience.replace(" ", "_").lower()]]
    if selected_jobtitle != "All":
        df = df.loc[df["General_info", "title_category"] == selected_jobtitle]
    if selected_size != "All":
        df = df.loc[df["General_info", "company_size"].map(size_groups) == selected_size]

    percentages = pd.Series(df[columns].mean() * 100, 
                            name=selected_requirements).sort_values(ascending=False).to_frame().head(20)
    if percentages.index.nlevels > 1:
        percentages = percentages.droplevel(0, axis=0)

    percentages.index = percentages.index.str.title()

    fig = px.bar(percentages,
             y=selected_requirements,
             x=percentages.index,
             color_discrete_sequence=['#1f77b4'],
             width=1000, height=500)

    fig.update_traces(
        hovertemplate="%{x}<br>Percentage: %{y:.1f}%<br><extra></extra>"
    )

    fig.update_layout(
        legend={"yanchor": "top", "y": 0.99, "xanchor": "right", "x": 0.99},
        xaxis_title=selected_requirements,
        yaxis_title="Percentages"
    )

    st.plotly_chart(fig)
