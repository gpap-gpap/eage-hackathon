import pandas as pd

dataframe = pd.read_excel(r"./data/Annual_2023_Hackathon_metadata.xlsx")


def recommendations(*, n: int, title: str):
    if n <= 0:
        result = "no recommendations"
    if title not in dataframe.Title:
        result = ["bullshit" for i in range(n)]
    else:
        result = ["bullshit" for i in range(n)]
    return result
