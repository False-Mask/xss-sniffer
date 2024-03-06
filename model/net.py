

class Request:
    header = dict()
    url: str = ""
    params: dict = dict()

    def __init__(self, header):
        self.header = header

    def __init__(self):
        pass


