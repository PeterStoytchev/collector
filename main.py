import json, logging, os

from cacher import Cached
from data import CarMeta
from filter import Filter, apply_filters

from datetime import datetime
from bs4 import BeautifulSoup as bs

logger = logging.getLogger()

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
        logger.info(f"Processing brand: {brand.name}")
        
        model_data = Cached(brand.link)
        models = get_all(model_data, [Filter("a", {"class": "modeli"})])

        for model in models:
            logger.info(f"Processing model: {model.name}")
            
            generations_data = Cached(model.link)
            generations = get_all(generations_data, [Filter("a", {"class": "position"})])

            for generation in generations:
                logger.debug(f"Processing generation: {generation.name}")

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
    if not os.path.exists("logs/"):
        os.mkdir("logs/")
    
    logging.basicConfig(filename=f'logs/trail-{int(datetime.now().timestamp())}.log', level=os.environ.get('LOGLEVEL', 'INFO').upper(), format="%(asctime)s;%(levelname)s;%(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    logger.info('Starting...')

    compute_car_links_to_file("links.json")

    logger.info('Fin!')

if __name__ == "__main__":
    main()