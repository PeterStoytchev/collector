import json

from cacher import Cached
from data import CarMeta
from filter import Filter, apply_filters

from bs4 import BeautifulSoup as bs

def get_all(resp: Cached, filters: list[Filter]) -> list:
    sp = bs(resp.text, "html.parser")

    elem = apply_filters(filters, sp)

    final_elements = []
    for x in elem:
        thing = CarMeta(x.text, x.get('href'))
        final_elements.append(thing)

    return final_elements

def compute_car_links_to_file(fname: str):
    brands_data = Cached("/en/allbrands")

    links = []

    brands = get_all(brands_data, [Filter("a", {"class": "marki_blok"})])
    for brand in brands:
        model_data = Cached(brand.link)
        models = get_all(model_data, [Filter("a", {"class": "modeli"})])

        for model in models:
            generations_data = Cached(model.link)
            generations = get_all(generations_data, [Filter("a", {"class": "position"})])

            for generation in generations:
                trim_data = Cached(generation.link)

                tb_filter = Filter("table", {"class": "carlist"})
                th_filter = Filter("th", {"class": "i"})
                pos_filter = Filter("a")
                trims = get_all(trim_data, [tb_filter, th_filter, pos_filter])

                for trim in trims:
                    links.append(trim.link)


    f = open(fname, "w", encoding="utf-8")
    f.write(json.dumps(links))
    f.close()

def main():
    compute_car_links_to_file("links.json")

if __name__ == "__main__":
    main()