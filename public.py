import streamlit as st
import pandas as pd
import basic_functions as bf

import query_scholar as qs

st.set_page_config(layout="wide")
st.session_state["recommendations"] = False


@st.cache_data
def load_data():
    return pd.read_excel(r"./data/Annual_2023_Hackathon_metadata.xlsx")


df = load_data()
df["Selected"] = False
recommendations = df[df["Selected"] == True]

st.title("EAGE 2023 abstract recommendation engine")

col1, col2 = st.columns([60, 60])
with col1:
    st.header("1. Select titles to base recommendations on")
    new_df = st.data_editor(
        df[["Title", "Selected"]],
        column_config={
            "favorite": st.column_config.CheckboxColumn(
                "Your favourite?",
                help="Select your **favourite** titles",
                default=False,
            )
        },
        disabled=["widgets"],
        hide_index=True,
    )
    if st.button("Reset recommendations"):
        recommendations = df[df["Selected"] == True]
    if st.button("Generate recommendations"):
        recommendations = df[new_df["Selected"] == True]
    n_recoms = st.radio("How many recommendations", [1, 5, 10])
with col2:
    st.header("2. These are your Recommendations")
    st.dataframe(recommendations)
    # st.write(recommendations["Title"].iloc[0])
    st.write(recommendations["Title"])
    # st.write(bf.recommendations(n=n_recoms, title=recommendations["Title"].iloc[0]))
search_term = st.text_input("Search term", "AVO inversion")
# new_data = qs.return_first_page(query=search_term)
# st.dataframe(new_data)

# def app():
#
