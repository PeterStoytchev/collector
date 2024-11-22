class CarMeta:
    def __init__(self, name: str, link: str):
        self.name = name.strip()
        self.link = link.strip()

    def __str__(self):
        return f"{self.name},{self.link}"
    
    def __repr__(self):
        return str(self)