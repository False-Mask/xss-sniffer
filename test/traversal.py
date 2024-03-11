import core.args
from core.scanner import *

reflect = "http://localhost:4280/vulnerabilities/xss_r/"
store = "http://localhost:4280/vulnerabilities/xss_s/"
dom = "http://localhost:4280/vulnerabilities/xss_d/"


def testForScanXSS():
    core.args.parse()
    req = cmdOpt.req

    # 反射
    # req.rawUrl = reflect

    # store
    # req.rawUrl = store

    # dom
    # req.rawUrl = dom
    # req.method = True

    req.header = {
        "Cookie": "language=en; security=low; PHPSESSID=4499bd47c63e45b14b79a6f70fc2b907"
    }
    scanXssForCurNode(req, get(req))


if __name__ == "__main__":
    def testForGetNodes():
        req: Request = Request()
        req.rawUrl = "https://docs.python.org/zh-cn/3.7/library/queue.html"
        req.parseUrl()
        req.convertParams()

        for node in getChildNodes(get(req).text, req):
            print("rawUrl:\t{raw}\nurl:\t{url}\n".format(raw=node.rawUrl, url=node.url))


    def testForTraversal():
        req: Request = Request()
        req.rawUrl = "http://localhost:4280/"
        req.header = {
            "Cookie":
                "language=en; welcomebanner_status=dismiss; cookieconsent_status=dismiss; Webstorm-96d8578f=06c8a379-1af9-49ec-8f09-5bacb0513889; Pycharm-4cb895e0=7e58d527-253a-44c5-a91d-9aa460d75850; security=low; PHPSESSID=4499bd47c63e45b14b79a6f70fc2b907"
        }
        req.timeout = 10
        req.parseUrl()
        req.convertParams()

        traversal(req)

    testForTraversal()

    # testForScanXSS()
