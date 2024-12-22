import os, random, time, uuid, logging

from pydo import Client

logger = logging.getLogger()

def create_droplet(client: Client, region_slug: str, size: str):
    droplet_name = f"test-{region_slug}-{size}-{str(uuid.uuid4())}"
    droplet_req = {
        "name": droplet_name,
        "region": region_slug,
        "size": size,
        "image": "173608349",
        "ssh_keys": ["ae:dd:ab:06:e4:ed:35:a5:8b:fa:a9:5c:e4:3a:fc:08"],
        "tags": ["collector"],
        "ipv6": False,
        "backups": False,
        "monitoring": True
    }
    resp = client.droplets.create(body=droplet_req)
    return (resp["droplet"]["id"], droplet_name)

class ProxyManager:
    def __init__(self, max_proxies: int = 2):
        self.client = Client(token=os.getenv("DIGITALOCEAN_TOKEN"))
        logging.getLogger('pydo').setLevel(logging.WARNING)
        logging.debug("Setup DigitalOcean client.")

        self.proxies = []
        self.current_index = 0

        self.client.droplets.destroy_by_tag(tag_name="collector")
        logging.info("Cleaned up existing collector instances.")

        useful_regions = self.compute_useful_regions()
        logging.debug(f"Working with regions: {useful_regions}")

        droplet_limit = self.client.account.get()["account"]["droplet_limit"] - len(self.client.droplets.list()["droplets"])
        droplet_ids = []
        for item in useful_regions:
            (droplet_id, droplet_name) = create_droplet(self.client, item["reg"], item["size"])
            droplet_ids.append(droplet_id)

            logging.info(f"Creating instance with {droplet_name} with id {droplet_id}")

            if len(droplet_ids) == droplet_limit or len(droplet_ids) == max_proxies:
                break

        for id in droplet_ids:
            self.proxies.append(Proxy(self.client, id))

        logging.info("Sleeping for 5 seconds, to give some time to squid to come up on all instances.")
        time.sleep(5)

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
            logging.info("All proxies have been iterated over, shuffling and resetting!")
            random.shuffle(self.proxies)
            self.current_index = 0

        final = self.proxies[self.current_index].get()
        self.current_index = self.current_index + 1

        logging.info(f"Selected proxy {final}.")
        return {
            "http": final,
            "https": final
        }
    
    def close(self):
        logging.info("Cleaning up instances.")
        self.client.droplets.destroy_by_tag(tag_name="collector")
    

class Proxy:
    def __init__(self, client: Client, droplet_id: str):
        self.droplet_id = droplet_id
        self.request_count = 0
        self.client = client

        self.addr = self.get_public_ip()
        
        logging.info(f"Proxy with droplet id {self.droplet_id} is up at address {self.addr}")


    def get_public_ip(self):
        resp = self.client.droplets.get(self.droplet_id)

        while resp["droplet"]["status"] != "active":
            logging.info(f"Droplet {resp['droplet']['name']} not ready. Sleeping for 10 seconds")
            time.sleep(10)
            resp = self.client.droplets.get(self.droplet_id)

        for net in resp["droplet"]["networks"]["v4"]:
            if net["type"] == "public":
                return net["ip_address"]

    def refresh(self):
        logging.info(f"Refreshing proxy {self.droplet_id} with ip {self.addr}")
        
        current_region = self.client.droplets.get(self.droplet_id)["droplet"]["region"]
        
        self.client.droplets.destroy(self.droplet_id)
        logging.info(f"Destoryed droplet {self.droplet_id}")

        (droplet_id, droplet_name) = create_droplet(self.client, current_region["slug"], current_region["sizes"][0])
        logging.info(f"Created new droplet {droplet_id} with name {droplet_name}")

        self.droplet_id = droplet_id
        self.request_count = 0
        self.addr = self.get_public_ip()
        
        logging.info(f"Proxy updated!")


    def get(self) -> str:
        logging.info(f"Proxy {self.droplet_id} is at {self.request_count} requests.")

        if self.request_count > os.environ.get("MAX_REQ_INSTANCE", 180):
            logging.info(f"Proxy {self.droplet_id} at {self.addr} has been used {self.request_count}. Refreshing!")
            
            self.refresh()
            self.request_count = 0

            logging.info(f"Proxy {self.droplet_id} has been refreshed! New addr is {self.addr}.")

        self.request_count = self.request_count + 1
        return f"http://{self.addr}:3128"