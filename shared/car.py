from opensearchpy import Document, IntegerRange, Text, Integer, Float, FloatRange

from bs4 import BeautifulSoup as bs

from filter import Filter, apply_filters
import json

def clean_str(text: str) -> str:
    return ' '.join(text.strip().split())

class Car:
    def __init__(self, html: str):
        super().__init__()
        self.parse(html)
    
    def parse(self, html: str):
        self.attrs = {}
        soup = bs(html, "html.parser")
        table_filter = Filter("table", {"class": "cardetailsout car2"})
        tr_filter = Filter("tr")
        
        elems = apply_filters([table_filter, tr_filter], soup)
        for x in elems:
            td = x.find_all("td")
            th = x.find_all("th")
            if len(td) != 0 and len(th) != 0:
                self.attrs[clean_str(th[0].text)] = clean_str(td[0].text)

    def to_json(self) -> str:
        return json.dumps(self.attrs)