import json, logging, os, sys, signal

from shared.cacher import Cached
from shared.car import Car
from shared.proxymanager import ProxyManager

from opensearchpy import OpenSearch

logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO').upper(), format="%(asctime)s;%(levelname)s;%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger()

pm = ProxyManager()

def exit_gracefully():
    pm.close()
    logger.info('Fin!')
    sys.exit(0)

def main():
    # Handle signals
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)
    
    if len(sys.argv) < 2:
        print("Usage: python list_collector.py <json_array_file>")
        sys.exit(1)

    logger.info('Starting...')

    f = open(sys.argv[1], "r", encoding="utf-8")
    data = json.loads(f.read())
    f.close()

    host = os.environ.get("OPENSEARCH_URI", None)

    if host is not None:
        client = OpenSearch(hosts=[], verify_certs = False, ssl_show_warn=False)
        try:
            client.indices.create('cars')
        except Exception as e:
            # Make sure that you have a fresh index every time you run
            client.indices.delete('cars')
            client.indices.create('cars')

    try:
        for car_link in data:
            car_data = Cached(car_link, pm)
            
            if host is not None:
                car = Car(car_data.text)
                client.index(index='cars', body=car.attrs)
    finally:
        exit_gracefully()

if __name__ == "__main__":
    main()