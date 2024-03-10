from core.scanner import *


req: Request = Request()
req.rawUrl = "https://docs.python.org/zh-cn/3.7/library/queue.html"
req.parseUrl()
req.convertParams()

for node in getChildNodes(get(req).text, req):
    print("rawUrl:\t{raw}\nurl:\t{url}\n".format(raw=node.rawUrl, url=node.url))

