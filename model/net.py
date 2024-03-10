import copy


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
            self.convertedParams = copy.deepcopy(self.params)
        else:
            self.convertedParams = copy.deepcopy(self.data)

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

