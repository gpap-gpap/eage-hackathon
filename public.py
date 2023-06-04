import streamlit as st
import pandas as pd
import basic_functions as bf

# import query_scholar as qs

st.set_page_config(layout="wide")
st.session_state["recommendations"] = False


@st.cache_data
def load_data():
    return pd.read_csv(r"./data/Annual_2023_Hackathon_metadata.csv")


df = load_data()
df["Selected"] = False
recommendations = df[df["Selected"] == True]

# @st.cache_data
ind_to_pdf = bf.load_dict()

st.title("EAGE 2023 abstract recommendation engine")
st.write(
    "<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;} </style>",
    unsafe_allow_html=True,
)

n_recoms = st.radio("How many recommendations?", [5, 10, 20])
col1, _, col2 = st.columns([60, 5, 60])
with col1:
    st.header("Papers to recommend from")
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
        recommendations = new_df["Selected"] == False
    if st.button("Generate recommendations"):
        recommendations = df[new_df["Selected"] == True]
        indices = recommendations["File name"].apply(bf.get_id_from_pdf).values

with col2:
    st.header("Our recommendations")
    # for i in indices:
    #     dictionary_out = bf.similarity_return_v3(id=i, n=n_recoms)
    #     st.write("this is what I am testing", f"{dictionary_out[0]['Title']}")
    # st.write(dictionary_out)
    # st.write(indices)
    # st.write([ind for ind in indices])
    id_list = bf.average_vectors(ids=list(indices))
    # st.write(id_list)
    results = bf.db_search(ids=list(indices), n=n_recoms)
    parsed = bf.parse_metadata(metadata=results)
    testdf = df.loc[df["File name"].isin(parsed)]
    st.dataframe(testdf["Title"], use_container_width=True, hide_index=True)
    # st.write(parsed)
    # st.dataframe(recommendations)
    # st.write(recommendations["Title"].iloc[0])
    # st.write(recommendations["Title"])
    # st.write(bf.recommendations(n=n_recoms, title=recommendations["Title"].iloc[0]))
# string = ""
# for i in indices:.replace(" ", "+")
# chunks = dictionary_out[0]["Title"]
# search_term = st.write("testing search term", chunks[1])

# new_data = qs.return_first_page(query=search_term)
# st.dataframe(new_data)

# def app():
#
