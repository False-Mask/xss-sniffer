from .net import Request


class CmdOpt:

    def __init__(self):
        self.req: Request = Request()
        self.encoding: str = ""
        self.skipDOM: bool = False
        self.skip: bool = False
        # sele
        self.useSele: bool = False
        self.enableUI: bool = False
        # crawl
        self.crawl: bool = False
        # fuzz
        self.fuzz: bool = False
