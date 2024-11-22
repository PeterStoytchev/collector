from bs4 import BeautifulSoup as bs

def get_last(ls: list) -> any:
    length = len(ls)
    return ls[length - 1]

def get_specific_element(element: str, source: str, filter: str) -> any:
    sp = bs(source, "html.parser")
    return sp.find_all(element, {"class": filter})