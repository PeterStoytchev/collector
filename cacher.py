import requests, hashlib, sys, time, random, os.path, logging

logger = logging.getLogger()

def env_sleep():
    sleep_min = os.getenv("SLEEP_MIN", 10)
    sleep_max = os.getenv("SLEEP_MAX", 30)

    sleep_ammount = random.randrange(sleep_min, sleep_max)
    logger.info(f"Sleeping for {sleep_ammount}")
    time.sleep(sleep_ammount)
    return

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
        logger.debug("Cache miss")

        env_sleep()

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