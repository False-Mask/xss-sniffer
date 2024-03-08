import time

import requests
from selenium import webdriver
from model.net import Request
from model.opt import CmdOpt

browser: webdriver.Chrome

clientInit: bool = False


def initClient(cmd: CmdOpt):
    # enable init once
    global clientInit
    if clientInit:
        return
    clientInit = True

    # init option
    options = webdriver.ChromeOptions()
    if not cmd.enableUI:
        options.add_argument("--headless")

    # init browser
    global browser
    browser = webdriver.Chrome(
        options=options,
        keep_alive=True
    )


def request(req: Request):
    url = req.url
    # add /
    if not url.endswith('/'):
        url += '/'
    # append kv
    for h in req.header:
        url += h[0] + "=" + h[1]
    browser.get(req.url)
    for head in req.header:
        if head[0] == "Cookie":
            v = head[1]
            kvs = v.split(";")
            for kv in kvs:
                keyValue = kv.split(":")
                browser.add_cookie({
                    "name": keyValue[0],
                    "value": keyValue[1],
                    "domain": "localhost",
                })

    browser.get("http://localhost:4280/vulnerabilities/xss_d/")
    return browser.page_source


# test
if __name__ == '__main__':
    from core.args import parse

    cmd = parse()
    initClient(cmd)
    request(cmd.req)
    time.sleep(100000)
