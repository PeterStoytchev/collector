import requests, hashlib, sys, time, random, os.path, logging
from shared.proxymanager import ProxyManager

from fake_useragent import UserAgent

logger = logging.getLogger()

def env_sleep():
    sleep_min = int(os.environ.get("SLEEP_MIN", 1))
    sleep_max = int(os.environ.get("SLEEP_MAX", 3))

    sleep_ammount = random.randrange(sleep_min, sleep_max)
    logger.info(f"Sleeping for {sleep_ammount}")
    time.sleep(sleep_ammount)
    return

class Cached:
    def __init__(self, url: str, proxy_manager: ProxyManager = None):
        self.url = f"https://www.auto-data.net{url}"
        self.thing = None
        self.proxy_manager = proxy_manager
        self.agent_faker = UserAgent()

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

        current_headers = {'User-Agent': str(self.agent_faker.random)}
        prx = None

        if self.proxy_manager is not None:
            prx = self.proxy_manager.get()

        while True:
            try:
                resp = requests.get(self.url, proxies=prx, headers=current_headers)
            except Exception as e:
                logging.info(f"Proxy {prx} not ready! Waiting for 10 seconds.")
                time.sleep(10)
            else:
                break

        if resp.status_code != 200:
            logger.fatal(f"Got {resp.status_code} from {self.url}. Exiting!")
            sys.exit(1)

        resp.encoding = resp.apparent_encoding

        f = open(self.__fname, "w", encoding="utf-8")
        
        f.write(resp.text)
        f.close()

        self.thing = resp.text

        env_sleep()

    @property
    def text(self) -> str:
        return str(self.thing)