from cacher import Cached
from data import MakeLink
from utils import get_specific_element

def get_all(resp: Cached, filter: str) -> list:

    sp_brands = get_specific_element("a", resp.text, filter)

    brands = []
    for x in sp_brands:
        thing = MakeLink(x.text.strip(), f"https://www.auto-data.net{x.get('href').strip()}")
        brands.append(thing)

    return brands

def main():
    resp = Cached("https://www.auto-data.net/en/allbrands")
    brands = get_all(resp, "marki_blok")
    for brand in brands:
        brand_data = Cached(brand.link)
        models = get_all(brand_data, "modeli")
        for x in models:
            print(x)
        

if __name__ == "__main__":
    main()