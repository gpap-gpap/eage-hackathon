import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from time import sleep
import pandas as pd

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}


def get_paperinfo(paper_url):
    # download the page
    response = requests.get(paper_url, headers=headers)

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
    link_tag = doc.find_all("h3", {"class": "gs_rt"})
    author_tag = doc.find_all("div", {"class": "gs_a"})
    text_tag = doc.find_all("div", {"class": "gs_rs"})
    return paper_tag, cite_tag, link_tag, author_tag, text_tag


def get_text(text_tag):
    texts = []
    for i in text_tag:
        texts.append(i.text)
    return texts


# function for the getting link information
def get_link(link_tag):
    links = []

    for i in range(len(link_tag)):
        links.append(link_tag[i].a["href"])

    return links


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
    "Url of paper": [],
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
    link,
    text,
):
    paper_repos_dict["Paper Title"].extend(papername)
    paper_repos_dict["Year"].extend(year)
    paper_repos_dict["Author"].extend(author)
    # # paper_repos_dict['Citation'].extend(cite)
    paper_repos_dict["Publication"].extend(publi)
    paper_repos_dict["Url of paper"].extend(link)
    paper_repos_dict["Text"].extend(text)
    return pd.DataFrame(paper_repos_dict)


def return_first_page(*, query: str):
    # final
    new_query = query.replace(" ", "+")
    url = f"https://scholar.google.com/scholar?start=0&q=EAGE+conference+and+exhibition+{new_query}&as_sdt=0,5"

    paper_repos_dict = {
        "Paper Title": [],
        "Year": [],
        "Author": [],
        # 'Citation' : [],
        "Publication": [],
        "Url of paper": [],
        "Text": [],
    }

    # function for the get content of each page
    doc = get_paperinfo(url)

    # function for the collecting tags
    paper_tag, cite_tag, link_tag, author_tag, text_tag = get_tags(doc)

    # paper title from each page
    papername = get_papertitle(paper_tag)

    # year , author , publication of the paper
    year, publication, author = get_author_year_publi_info(author_tag)

    text = get_text(text_tag)
    # cite count of the paper
    # cite = get_citecount(cite_tag)

    # url of the paper
    link = get_link(link_tag)

    # add in paper repo dict
    final = add_in_paper_repo(papername, year, author, publication, text, link)

    # use sleep to avoid status code 429
    result = [final["Paper Title"].iloc[0], final["Url of paper"].iloc[0]]
    return final
