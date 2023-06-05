import streamlit as st
import pandas as pd
import basic_functions as bf
from streamlit.components.v1 import html
import query_scholar as qs
from PIL import Image

image = Image.open("eagle_transparent.png")

st.set_page_config(layout="wide")


def open_page(url):
    open_script = """
        <script type="text/javascript">
            window.open('%s', '_blank').focus();
        </script>
    """ % (
        url
    )
    html(open_script)


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
col1, _, col2 = st.columns([100, 5, 20])
with col1:
    st.title("EAGE 2023 abstract recommendation engine")
with col2:
    st.image("eagle_icon.png", width=200)
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
    st.header("Make sure to check out...")

    if st.session_state.current_indices == []:
        st.write("First, please select some papers to recommend from")
    else:
        id_list = bf.average_vectors(ids=list(st.session_state.current_indices))
        id = st.session_state.current_indices[0]

        n = n_recoms + len(st.session_state.current_indices)
        results = bf.db_search(ids=list(st.session_state.current_indices), n=n)[
            len(st.session_state.current_indices) :
        ]
        parsed = bf.parse_metadata(metadata=results)
        testdf = df.loc[df["File name"].isin(parsed)]
        for index, row in testdf.iterrows():
            with st.expander(row["Title"]):
                text = st.markdown(f"_{row['Summary']}_")

        cont, _ = qs.parse_db_result(
            results=qs.db_search(ids=st.session_state.search_indices, n=n)
        )
        wf = qs.word_frequency(cont).most_common(10)
        query, readable = qs.create_query(cont)
        st.write(readable)
        url = qs.return_first_page(query=query)
        if st.button("...as well as these past EAGE classic papers!"):
            open_page(url)

st.header("Search by query")

prev_qry = "avo"
user_query = st.text_input(label="")
if st.button("Search in EAGE '23 papers") or (prev_qry != user_query):
    prev_qry = user_query
    results_fromsearch = bf.search_by_query(user_query, n_recoms)
    parsed_fromsearch = bf.parse_metadata(metadata=results_fromsearch)
    returned_df = df.loc[df["File name"].isin(parsed_fromsearch)]

    for index, row in returned_df.iterrows():
        with st.expander(row["Title"]):
            text = st.markdown(f"_{row['Summary']}_")
