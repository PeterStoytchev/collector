import os, random, time, uuid

from pydo import Client

class ProxyManager:
    def __init__(self, max_proxies: int = 2):
        self.client = Client(token=os.getenv("DIGITALOCEAN_TOKEN"))

        self.proxies = []
        self.current_index = 0

        self.client.droplets.destroy_by_tag(tag_name="collector")

        useful_regions = self.compute_useful_regions()
        
        droplet_limit = self.client.account.get()["account"]["droplet_limit"] - len(self.client.droplets.list()["droplets"])
        droplet_ids = []
        for item in useful_regions:
            droplet_req = {
                "name": f"test-{item['reg']}-{item['size']}-{str(uuid.uuid4())}",
                "region": item['reg'],
                "size": item['size'],
                "image": "173608349",
                "ssh_keys": ["ae:dd:ab:06:e4:ed:35:a5:8b:fa:a9:5c:e4:3a:fc:08"],
                "tags": ["collector"],
                "ipv6": False,
                "backups": False,
                "monitoring": True
            }
            resp = self.client.droplets.create(body=droplet_req)
            
            droplet_id = resp["droplet"]["id"]
            droplet_ids.append(droplet_id)

            if len(droplet_ids) == droplet_limit or len(droplet_ids) == max_proxies:
                break

        for id in droplet_ids:
            self.proxies.append(Proxy(self.client, id))

        time.sleep(10)

    def compute_useful_regions(self):
        regions = self.client.regions.list()
        useful_regions = []
        for reg in regions["regions"]:
            sizes = reg['sizes']
            if len(sizes) > 0 and reg['available']:
                useful_regions.append({"reg": reg['slug'], "size": sizes[0]})

        random.shuffle(useful_regions)
        return useful_regions

    def get(self) -> dict:
        if self.current_index == len(self.proxies):
            random.shuffle(self.proxies)
            self.current_index = 0

        final = self.proxies[self.current_index].get()
        self.current_index = self.current_index + 1

        return {
            "http": final,
            "https": final
        }
    
    def close(self):
        self.client.droplets.destroy_by_tag(tag_name="collector")
    

class Proxy:
    def __init__(self, client: Client, droplet_id: str):
        self.droplet_id = droplet_id
        self.request_count = 0
        self.client = client

        self.addr = self.get_public_ip()


    def get_public_ip(self):
        resp = self.client.droplets.get(self.droplet_id)

        while resp["droplet"]["status"] != "active":
            print(f"Droplet {resp['droplet']['name']} not ready. Sleeping for 20 seconds")
            time.sleep(5)
            resp = self.client.droplets.get(self.droplet_id)

        for net in resp["droplet"]["networks"]["v4"]:
            if net["type"] == "public":
                return net["ip_address"]

    def refresh(self):
        pass

    def get(self) -> str:
        if self.request_count > os.environ.get("MAX_REQ_INSTANCE", 180):
            self.refresh()
            self.request_count = 0

        self.request_count = self.request_count + 1
        
        return f"http://{self.addr}:3128"