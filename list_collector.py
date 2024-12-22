import json, logging, os, sys

from shared.cacher import Cached
from shared.car import Car

from opensearchpy import OpenSearch

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

    client = OpenSearch(hosts=[os.environ.get("OPENSEARCH_URI")], verify_certs = False, ssl_show_warn=False)
    try:
        client.indices.create('cars')
    except Exception as e:
        pass

    for car_link in data:
        car_data = Cached(car_link)
        car = Car(car_data.text)
        client.index(index='cars', body=car.attrs)


    logger.info('Fin!')

if __name__ == "__main__":
    main()