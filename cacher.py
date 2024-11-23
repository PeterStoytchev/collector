import requests, hashlib, sys, time, random, os.path, logging

logger = logging.getLogger()

GLOBAL_REQUEST_COUNTER = 0

def sleep_needed():
    sleep_ammount = None
    if GLOBAL_REQUEST_COUNTER == random.randrange(40, 60):
        sleep_ammount = random.randrange(10, 15)
        GLOBAL_REQUEST_COUNTER = 0
    else:
        sleep_ammount = 4

    GLOBAL_REQUEST_COUNTER = GLOBAL_REQUEST_COUNTER + 1
    
    time.sleep(sleep_ammount)
    logger.info(f"Sleeping for {sleep_ammount}")

class Cached:
    def __init__(self, url: str):
        self.url = f"https://www.auto-data.net{url}"
        self.thing = None

        self.__fname = f"cache/{hashlib.md5(self.url.encode()).hexdigest()}.cache"

        if os.path.exists("cache/"):
            if os.path.isfile(self.__fname):
                f = open(self.__fname, "r", encoding="utf-8")
                self.thing = f.read()
                f.close()
                return
        else:
            os.mkdir("cache/")
        
        self.refresh()

    def refresh(self):
        logger.warn("Cache miss")

        sleep_needed()

        resp = requests.get(self.url)
        if resp.status_code == 429:
            logger.fatal(f"Got 429 from {self.url}")
            sys.exit(1)

        resp.encoding = resp.apparent_encoding

        f = open(self.__fname, "w", encoding="utf-8")
        
        f.write(resp.text)
        f.close()

        self.thing = resp.text

    @property
    def text(self) -> str:
        return str(self.thing)