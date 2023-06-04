import streamlit as st
import pandas as pd
import basic_functions as bf

import query_scholar as qs


st.set_page_config(layout="wide")

page_bg_img = """
<style>
body {
background-image: url("https://images.unsplash.com/photo-1542281286-9e0a16bb7366");
background-size: cover;
}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)


if "recommendations" not in st.session_state:
    st.session_state.recommendations = False
if "current_indices" not in st.session_state:
    st.session_state.current_indices = []
if "search_indices" not in st.session_state:
    st.session_state.search_indices = []


def reset():
    st.session_state.recommendations = False
    st.session_state.current_indices = []


@st.cache_data
def load_data():
    return pd.read_csv(r"./data/Annual_2023_Hackathon_metadata.csv")


df = load_data()
df["Selected"] = False
st.session_state.recommendations = df[df["Selected"] == True]

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
    st.header("Which EAGE '23 papers do you like?")
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
        st.session_state.recommendations = df[new_df["Selected"] == False]
    if st.button("Generate recommendations"):
        st.session_state.recommendations = df[new_df["Selected"] == True]
        st.session_state.current_indices = (
            st.session_state.recommendations["File name"]
            .apply(bf.get_id_from_pdf)
            .values
        )
        st.session_state.search_indices = (
            st.session_state.recommendations["File name"]
            .apply(qs.get_id_from_pdf_chunks)
            .values
        )

with col2:
    st.header("Also check out...")
    # for i in indices:
    #     dictionary_out = bf.similarity_return_v3(id=i, n=n_recoms)
    #     st.write("this is what I am testing", f"{dictionary_out[0]['Title']}")
    # st.write(dictionary_out)
    # st.write(indices)
    # st.write([ind for ind in indices])
    if st.session_state.current_indices == []:
        st.write("First, please select some papers to recommend from")
    else:
        id_list = bf.average_vectors(ids=list(st.session_state.current_indices))
        id = st.session_state.current_indices[0]
        # st.write("indices", bf.return_vector(id=id))
        # st.write(id_list)
        n = n_recoms + len(st.session_state.current_indices)
        results = bf.db_search(ids=list(st.session_state.current_indices), n=n)[
            len(st.session_state.current_indices) :
        ]
        parsed = bf.parse_metadata(metadata=results)
        testdf = df.loc[df["File name"].isin(parsed)]
        st.dataframe(testdf["Title"], use_container_width=True, hide_index=True)

    # st.write(parsed)
    # st.dataframe(recommendations)
    # st.write(recommendations["Title"].iloc[0])
    # st.write(recommendations["Title"])
    # st.write(bf.recommendations(n=n_recoms, title=recommendations["Title"].iloc[0]))
    st.header("...as well as these classics!")
    if st.session_state.search_indices == []:
        st.write("First, please select some papers to recommend from")
    else:
        cont, _ = qs.parse_db_result(
            results=qs.db_search(ids=st.session_state.current_indices, n=15)
        )
        wf = qs.word_frequency(cont).most_common(6)
        query, readable = qs.create_query(cont)
        st.write(readable)
        # if st.button("Search"):
        # new_data = qs.return_first_page(query=query)
        # st.dataframe(new_data)
# string = ""
# for i in indices:.replace(" ", "+")
# chunks = dictionary_out[0]["Title"]
# search_term = st.write("testing search term", chunks[1])

# new_data = qs.return_first_page(query=search_term)
# st.dataframe(new_data)

# def app():
