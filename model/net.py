

class Request:
    # False -> GET, True -> POST
    method: bool = False
    header = dict()
    rawUrl: str = ""
    url: str = ""
    params: dict = dict()
    delay: int = 0
    data: dict = dict()
    timeout: int = 0



    def __init__(self, header):
        self.header = header

    def __init__(self):
        pass


