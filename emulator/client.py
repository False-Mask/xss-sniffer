import time
import urllib.parse
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
    if not url.endswith('?'):
        url += '?'
    # append kv
    for (k, v) in req.params.items():
        url += k + "=" + v
    browser.get(req.url)
    parseResult = urllib.parse.urlparse(url)
    domain = parseResult.netloc.split(':')[0]
    for (headkey, headValue) in req.header.items():
        if headkey == "Cookie":
            v = headValue
            kvs = v.split(";")
            for kv in kvs:
                keyValue = kv.split("=")
                if len(keyValue) < 2:
                    break
                browser.add_cookie({
                    "name": keyValue[0].strip(),
                    "value": keyValue[1].strip(),
                    "domain": domain,
                })

    browser.get(url)
    return browser.page_source


# test
if __name__ == '__main__':
    from core.args import parse

    cmd = parse()
    initClient(cmd)
    print(request(cmd.req))
    time.sleep(100000)
