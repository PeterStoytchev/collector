class MakeLink:
    def __init__(self, make: str, link: str):
        self.make = make
        self.link = link

    def __str__(self):
        return f"{self.make},{self.link}"
    
    def __repr__(self):
        return str(self)