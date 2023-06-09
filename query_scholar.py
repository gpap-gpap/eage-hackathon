import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from time import sleep
import pandas as pd
import os
import nltk
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain import schema as langchain_schema
import string
import openai
import streamlit as st

nltk.download("stopwords")
nltk.download("punkt")
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from nltk.tokenize import sent_tokenize


stop_words = set(stopwords.words("english"))
years = {str(i) for i in range(1996, 2022)}

openai_api_key = st.secrets["PAID_OPEN_AI"]
# openai.api_key = "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"
embeddings = OpenAIEmbeddings()
db = FAISS.load_local(
    "./vectordb/eage_annual_2023_chunks_basic_test/",
    embeddings,
)

pdf_to_id_chunks = {
    value.metadata["source"].rsplit("\\", 1)[-1]: index
    for index, value in enumerate(db.docstore._dict.values())
}


def get_id_from_pdf_chunks(pdf_number):
    if pdf_number not in pdf_to_id_chunks:
        print("pdf not found")
        result = None
    result = pdf_to_id_chunks.get(pdf_number)
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


def word_frequency(contents: list):
    test_text = [
        t.translate(str.maketrans("", "", string.punctuation)) for t in contents
    ]
    test_text = [t.lower() for t in test_text]
    tokenized_words = [word_tokenize(t) for t in test_text]
    flattened = [item for sublist in tokenized_words for item in sublist]
    # filtered_text = [w for w in word if w not in stop_words] for word in tokenized_words]
    my_words = {
        "paper",
        "results",
        "used",
        "method",
        "application",
        "figure",
        "fig",
        "et",
        "al",
        "annual",
        "conference",
        "exhibition",
        "eage",
        "journal",
    }
    filtered_text_2 = [
        w
        for w in flattened
        if w not in stop_words and w not in my_words and w not in years
    ]
    # filtered_text_3 = "".join(
    #     [i for word in filtered_text_2 for i in word if not i.isdigit()]
    # )
    filtered_text_3 = [word for word in filtered_text_2 if len(word) > 1]
    fdist = FreqDist(filtered_text_3)
    return fdist


def create_query(content):
    str = ""
    readable = ""
    for word, freq in word_frequency(content).most_common(5):
        str += word + "+"
        readable += word + " + "
    return str[:-1], readable[:-3]


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}


def get_paperinfo(paper_url):
    # download the page
    response = requests.get(paper_url, headers=headers)
    print(response.status_code)
    # check successful response
    if response.status_code != 200:
        print("Status code:", response.status_code)
        raise Exception("Failed to fetch web page ")

    # parse using beautiful soup
    paper_doc = BeautifulSoup(response.text, "html.parser")

    return paper_doc


def get_author_year_publi_info(authors_tag):
    years = []
    publication = []
    authors = []
    for i in range(len(authors_tag)):
        authortag_text = (authors_tag[i].text).split()
        year = int(re.search(r"\d+", authors_tag[i].text).group())
        years.append(year)
        publication.append(authortag_text[-1])
        author = authortag_text[0] + " " + re.sub(",", "", authortag_text[1])
        authors.append(author)

    return years, publication, authors


# this function for the extracting information of the tags
def get_tags(doc):
    paper_tag = doc.select("[data-lid]")
    cite_tag = doc.select("[title=Cite] + a")
    # link_tag = doc.find_all("h3", {"class": "gs_rt"})
    author_tag = doc.find_all("div", {"class": "gs_a"})
    text_tag = doc.find_all("div", {"class": "gs_rs"})
    return paper_tag, author_tag, text_tag


def get_text(text_tag):
    texts = []
    for i in text_tag:
        texts.append(i.text)
    return texts


# function for the getting link information
# def get_link(link_tag):
#     links = []

#     for i in range(len(link_tag)):
#         links.append(link_tag[i].a["href"])

#     return links


# it will return the number of citation of the paper
def get_citecount(cite_tag):
    cite_count = []
    for i in cite_tag:
        cite = i.text
        if i is None or cite is None:  # if paper has no citatation then consider 0
            cite_count.append(0)
        else:
            tmp = re.search(
                r"\d+", cite
            )  # its handle the None type object error and re use to remove the string " cited by " and return only integer value
            if tmp is None:
                cite_count.append(0)
            else:
                cite_count.append(int(tmp.group()))

    return cite_count


# it will return the title of the paper
def get_papertitle(paper_tag):
    paper_names = []

    for tag in paper_tag:
        paper_names.append(tag.select("h3")[0].get_text())

    return paper_names


paper_repos_dict = {
    "Paper Title": [],
    "Year": [],
    "Author": [],
    # 'Citation' : [],
    "Publication": [],
    # "Url of paper": [],
    "Text": [],
}


# adding information in repository
def add_in_paper_repo(
    papername,
    year,
    author
    # ,cite
    ,
    publi,
    # link,
    text,
):
    paper_repos_dict["Paper Title"].extend(papername)
    paper_repos_dict["Year"].extend(year)
    paper_repos_dict["Author"].extend(author)
    # # paper_repos_dict['Citation'].extend(cite)
    paper_repos_dict["Publication"].extend(publi)
    # paper_repos_dict["Url of paper"].extend(link)
    paper_repos_dict["Text"].extend(text)
    return pd.DataFrame(paper_repos_dict)


def return_first_page(*, query: str):
    # final
    new_query = query.replace(" ", "+")
    url = f"https://scholar.google.com/scholar?start=0&q=EAGE+conference+and+exhibition+{new_query}&as_sdt=0,5"

    # paper_repos_dict = {
    #     "Paper Title": [],
    #     "Year": [],
    #     "Author": [],
    #     # 'Citation' : [],
    #     "Publication": [],
    #     # "Url of paper": [],
    #     "Text": [],
    # }

    # def add_in_paper_repo(
    #     papername,
    #     year,
    #     author
    #     # ,cite
    #     ,
    #     publi,
    #     # link,
    #     text,
    # ):
    #     paper_repos_dict["Paper Title"].extend(papername)
    #     paper_repos_dict["Year"].extend(year)
    #     paper_repos_dict["Author"].extend(author)
    #     # # paper_repos_dict['Citation'].extend(cite)
    #     paper_repos_dict["Publication"].extend(publi)
    #     # paper_repos_dict["Url of paper"].extend(link)
    #     paper_repos_dict["Text"].extend(text)
    #     return pd.DataFrame(paper_repos_dict)

    # function for the get content of each page
    # doc = get_paperinfo(url)

    # function for the collecting tags
    # paper_tag, author_tag, text_tag = get_tags(doc)

    # # paper title from each page
    # papername = get_papertitle(paper_tag)

    # # year , author , publication of the paper
    # year, publication, author = get_author_year_publi_info(author_tag)

    # text = get_text(text_tag)
    # # cite count of the paper
    # # cite = get_citecount(cite_tag)

    # # url of the paper
    # # link = get_link(link_tag)

    # # add in paper repo dict
    # final = add_in_paper_repo(papername, year, author, publication, text)

    # use sleep to avoid status code 429
    # result = [final["Paper Title"].iloc[0], final["Url of paper"].iloc[0]]

    return url
