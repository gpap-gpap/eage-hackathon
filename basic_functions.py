import pandas as pd
import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain import schema as langchain_schema
import openai
import streamlit as st

pd.options.display.max_colwidth = 20
df = pd.read_excel(r"./data/Annual_2023_Hackathon_metadata.xlsx")
api_key = st.secrets["PAID_OPEN_AI"]
#
embeddings = OpenAIEmbeddings()
db = FAISS.load_local(
    "./vectordb/eage_annual_2023_summaries_basic_test/",
    embeddings,
)
pdf_to_id = {
    value.metadata["source"].rsplit("\\", 1)[-1]: index
    for index, value in enumerate(db.docstore._dict.values())
}


def load_dict():
    file_names = df["File name"].values
    result = {i: file_names[i][:-4] for i in df.index}
    return result


def return_vector_old(*, id: int):
    result = db.index.reconstruct_n(n0=id, ni=1)
    return result


def return_vector(*, id: int):
    result = db.index.reconstruct(key=int(id))
    return result


def average_vectors(*, ids: list):
    vectors = [return_vector(id=id) for id in ids]
    result = [sum(i) / len(i) for i in zip(*vectors)]
    return result


def db_search(*, ids: list, n: int):
    result = db.similarity_search_by_vector(average_vectors(ids=ids), k=n)
    return result


def parse_db_result(*, results: langchain_schema.Document):
    content = [result.page_content for result in results]
    metadata = [result.metadata for result in results]
    return content, metadata


def parse_metadata(*, metadata: langchain_schema.Document):
    contents, metadata = parse_db_result(results=metadata)
    get_pdfs = [string["source"].rsplit("\\", 1)[-1] for string in metadata]
    return get_pdfs


def get_id_from_pdf(pdf_number):
    if pdf_number not in pdf_to_id:
        print("pdf not found")
        result = None
    result = pdf_to_id.get(pdf_number)
    return result


def get_id_list_from_pdf_list(pdf_list):
    result = [
        get_id_from_pdf(pdf_number)
        for pdf_number in pdf_list
        if get_id_from_pdf(pdf_number) is not None
    ]
    return result


def search_by_query(query, n: int):
    # openai.api_key = "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"
    openai.api_key = st.secrets["PAID_OPEN_AI"]
    # openai.api_key = os.environ["PAID_OPEN_AI_KEY"]
    response = openai.Embedding.create(input=query, model="text-embedding-ada-002")
    embedding = response["data"][0]["embedding"]
    results = db.similarity_search_by_vector(embedding, k=n)

    return results
