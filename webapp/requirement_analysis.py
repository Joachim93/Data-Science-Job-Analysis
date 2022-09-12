import streamlit as st
import pandas as pd
import plotly.express as px


def requirements_analysis(df):
    st.title("Requirements for Data Science Jobs in Germany")
    col1, col2, col3 = st.columns(3)
    choices_job = ["All"] + list(df["General_info", "title_category"].unique())
    choices_requirement = df.columns.unique(0).drop("General_info")

    with col1:
        selected_skills = st.selectbox("Which Information are you interested in?", choices_requirement)

    with col2:
        first_choice = st.selectbox("Which jobtitle are you interested in?", choices_job)

    choices_new = [choice for choice in choices_job if choice != first_choice]

    with col3:
        second_choice = st.selectbox("Choose a second jobtitle (optional)", ["None"] + choices_new)

    if second_choice == "None":
        choices_selected = [first_choice]
    else:
        choices_selected = [first_choice, second_choice]

    if first_choice != "All":
        df_first = df.loc[df["General_info", "title_category"] == first_choice]
    else:
        df_first = df

    percentages_first = pd.Series(df_first[choices_requirement].sum() * 100 / len(df_first),
                                  name=first_choice).to_frame()

    if second_choice == "None":
        percentages = percentages_first
    else:
        if second_choice != "All":
            df_second = df.loc[df["General_info", "title_category"] == second_choice]
        else:
            df_second = df
        percentages_second = pd.Series(df_second[choices_requirement].sum() * 100 / len(df_second),
                                       name=second_choice).to_frame()
        percentages = pd.merge(percentages_first, percentages_second, left_index=True, right_index=True)

    percentages[first_choice] = percentages[first_choice].apply(lambda x: round(x, 2))
    if second_choice != "None":
        percentages = percentages.loc[(percentages[first_choice] > 0) | (percentages[second_choice] > 0)]
        percentages[second_choice] = percentages[second_choice].apply(lambda x: round(x, 2))
    else:
        percentages = percentages.loc[percentages[first_choice] > 0]
    percentages = percentages.sort_values(choices_selected, ascending=False)

    percentages = percentages.loc[selected_skills]

    fig = px.bar(percentages,
                 x=percentages.index,
                 y=choices_selected,
                 labels={"value": "Percentages", "index": selected_skills, "variable": "job title"},
                 barmode="group",
                 width=1050, height=500)
    fig.update_layout(legend={"yanchor": "top", "y": 0.99, "xanchor": "right", "x": 0.99})
    st.plotly_chart(fig)
