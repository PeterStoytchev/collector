import requests, hashlib
import os.path

class Cached:
    def __init__(self, url: str):
        self.url = url
        self.thing = None

        self.__fname = f"cache/{hashlib.md5(url.encode()).hexdigest()}.cache"

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
        resp = requests.get(self.url)
        resp.encoding = resp.apparent_encoding

        f = open(self.__fname, "w", encoding="utf-8")
        
        f.write(resp.text)
        f.close()

        self.thing = resp.text

    @property
    def text(self) -> str:
        return str(self.thing)