import copy


class Request:
    def __init__(self):
        # False -> POST, True -> GET
        self.method: bool = False
        self.header = dict()
        self.rawUrl: str = ""
        self.url: str = ""
        self.params: dict = dict()  # get params
        self.delay: int = 0
        self.data: dict = dict()  # post params
        self.timeout: int = 0
        # 转换后的参数
        self.convertedParams: dict = dict()
        # 不需要爆破的 kv 参数列表
        self.fixParams: dict[str, str] = dict()

    def convertParams(self):
        if self.method:
            self.convertedParams = copy.deepcopy(self.params)
        else:
            self.convertedParams = copy.deepcopy(self.data)

    def getFullParams(self):
        full: dict[str, str] = self.convertedParams
        # addFull
        for (k, v) in self.fixParams.items():
            full[k] = v
        return full

    def parseUrl(self):
        if self.rawUrl.find('?') > 0:
            split = self.rawUrl.split('?')
            self.url = split[0]
            if len(split) == 2:
                params = split[1].split('&')
                for param in params:
                    kv = param.split('=')
                    if len(kv) < 2:
                        kv.append('')
                    self.params[kv[0]] = kv[1]
        else:
            self.url = self.rawUrl


class RequestResult:

    def __init__(self):
        self.content = ""
        self.check = False
