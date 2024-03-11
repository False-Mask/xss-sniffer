from core.scanner import *

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
                "language=en; welcomebanner_status=dismiss; cookieconsent_status=dismiss; Webstorm-96d8578f=06c8a379-1af9-49ec-8f09-5bacb0513889; Pycharm-4cb895e0=7e58d527-253a-44c5-a91d-9aa460d75850; security=impossible; PHPSESSID=4499bd47c63e45b14b79a6f70fc2b907"
        }
        req.timeout = 10
        req.parseUrl()
        req.convertParams()

        traversal(req)

    testForTraversal()

