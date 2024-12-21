import json, logging, os, random, sys

from shared.cacher import Cached
from shared.filter import Filter, apply_filters
from shared.car import Car

from datetime import datetime
from bs4 import BeautifulSoup as bs

logger = logging.getLogger()

def main():
    if len(sys.argv) < 2:
        print("Usage: python list_collector.py <json_array_file>")
        sys.exit(1)

    logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO').upper(), format="%(asctime)s;%(levelname)s;%(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    logger.info('Starting...')

    f = open(sys.argv[1], "r", encoding="utf-8")
    data = json.loads(f.read())
    f.close()

    car_link = data[0]
    car_data = Cached(car_link)
    car = Car(car_data.text)
    # TODO: car.to_json() -> OpenSearch

    logger.info('Fin!')

if __name__ == "__main__":
    main()