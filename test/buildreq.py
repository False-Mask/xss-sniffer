from core.scanner import buildRequest, get
from model.net import Request

reflect = "http://localhost:4280/vulnerabilities/xss_r/"
store = "http://localhost:4280/vulnerabilities/xss_s/"
dom = "http://localhost:4280/vulnerabilities/xss_d/"

if __name__ == '__main__':
    req = Request()
    # 反射
    # req.rawUrl = reflect

    # store
    # req.rawUrl = store

    # dom
    req.rawUrl = dom

    req.method = True


    req.header = {
        "Cookie": "language=en; security=low; PHPSESSID=4499bd47c63e45b14b79a6f70fc2b907"
    }
    newReq = buildRequest(req, get(req).text)
    print("url: {url}\nparams: {params}".format(url=newReq.rawUrl, params=str(newReq.convertedParams)))
