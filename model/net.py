class Request:
    # False -> POST, True -> GET
    method: bool = False
    header = dict()
    rawUrl: str = ""
    url: str = ""
    params: dict = dict()  # get params
    delay: int = 0
    data: dict = dict()  # post params
    timeout: int = 0

    # 转换后的参数
    convertedParams: dict

    def convertParams(self):
        if self.method:
            self.convertedParams = self.params
        else:
            self.convertedParams = self.data

