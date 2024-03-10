import urllib.parse
from typing import Dict, Any, Type

import requests
from selenium import webdriver
from selenium.common import UnexpectedAlertPresentException, WebDriverException, NoAlertPresentException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.errorhandler import ErrorHandler, ErrorCode, ExceptionMapping

import core
from core.conf import timeout
from model.net import Request, RequestResult
from model.opt import CmdOpt

browser: webdriver.Chrome
wait: WebDriverWait

clientInit: bool = False


class ClientErrorHandler(ErrorHandler):

    def check_response(self, response: Dict[str, Any]) -> None:
        global browser
        status = response.get("status", None)
        if not status or status == ErrorCode.SUCCESS:
            return
        value = None
        message = response.get("message", "")
        screen: str = response.get("screen", "")
        stacktrace = None
        if isinstance(status, int):
            value_json = response.get("value", None)
            if value_json and isinstance(value_json, str):
                import json

                try:
                    value = json.loads(value_json)
                    if len(value) == 1:
                        value = value["value"]
                    status = value.get("error", None)
                    if not status:
                        status = value.get("status", ErrorCode.UNKNOWN_ERROR)
                        message = value.get("value") or value.get("message")
                        if not isinstance(message, str):
                            value = message
                            message = message.get("message")
                    else:
                        message = value.get("message", None)
                except ValueError:
                    pass

        exception_class: Type[WebDriverException]
        e = ErrorCode()
        error_codes = [item for item in dir(e) if not item.startswith("__")]
        for error_code in error_codes:
            error_info = getattr(ErrorCode, error_code)
            if isinstance(error_info, list) and status in error_info:
                exception_class = getattr(ExceptionMapping, error_code, WebDriverException)
                break
        else:
            exception_class = WebDriverException

        if not value:
            value = response["value"]
        if isinstance(value, str):
            raise exception_class(value)
        if message == "" and "message" in value:
            message = value["message"]

        screen = None  # type: ignore[assignment]
        if "screen" in value:
            screen = value["screen"]

        stacktrace = None
        st_value = value.get("stackTrace") or value.get("stacktrace")
        if st_value:
            if isinstance(st_value, str):
                stacktrace = st_value.split("\n")
            else:
                stacktrace = []
                try:
                    for frame in st_value:
                        line = frame.get("lineNumber", "")
                        file = frame.get("fileName", "<anonymous>")
                        if line:
                            file = f"{file}:{line}"
                        meth = frame.get("methodName", "<anonymous>")
                        if "className" in frame:
                            meth = f"{frame['className']}.{meth}"
                        msg = "    at %s (%s)"
                        msg = msg % (meth, file)
                        stacktrace.append(msg)
                except TypeError:
                    pass
        if exception_class == UnexpectedAlertPresentException:
            alert_text = None
            if "data" in value:
                alert_text = value["data"].get("text")
            elif "alert" in value:
                alert_text = value["alert"].get("text")
            browser.switch_to.alert.accept()
        else:
            raise exception_class(message, screen, stacktrace)


def initClient(cmd: CmdOpt):
    # enable init once
    global clientInit
    if clientInit:
        return
    clientInit = True

    # init option
    options = webdriver.ChromeOptions()
    # prefs = {'profile.default_content_setting_values': {'notifications': 2}}
    # options.set_capability("prefs", prefs)
    # options.set_capability("unhandledPromptBehavior", "ignore")
    if not cmd.enableUI:
        options.add_argument("--headless")
    # init browser
    global browser
    browser = webdriver.Chrome(
        options=options,
        keep_alive=True
    )
    # exec cpd cmd
    code = """
    hacked = false
    
    window.alert = function(message) {
    hacked = true
    };
    
    window.confirm = function (message) {
    hacked = true
    }"""
    browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {"source": code})
    # browser.error_handler = ClientErrorHandler()
    global wait
    wait = WebDriverWait(browser, 10)


def buildUrl(req: Request) -> str:
    url = req.url
    # Get
    if req.method:
        # add /
        if not url.endswith('/'):
            url += '/'
        if len(req.convertedParams) > 0 and not url.endswith('?'):
            url += '?'
        # append kv
        for (k, v) in req.convertedParams.items():
            url += k + "=" + v
    else:  # Post
        pass  # Do nothing
    return url


def addCookie(req: Request, url: str):
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


def paramsToString(params: dict[str, str]):
    data: str = ""
    i = 0
    for (k, v) in params.items():
        data += k + '=' + v
        i += 1
        if i != len(params):
            data += "&"
    return data


def execJsPostMethod(req: Request):
    prams = req.convertedParams
    data = paramsToString(prams)
    code = """
    const xhr = new XMLHttpRequest();
    const url={url};
    xhr.open("POST", url, false);
    xhr.send({data});
    """.format(url='"' + urllib.parse.urlparse(req.url).path + '"', data='"' + data + '"') + """
      xhr.onreadystatechange = function() {
        if (xhr.status === 200) {
            console.log(xhr.responseText);
        } else {
            console.log(xhr.status, xhr.responseText);
        }
    };"""
    v = browser.execute_script(code)
    pass


def request(req: Request, res: RequestResult) -> str:
    # wait.until(expected_conditions.presence_of_element_located())
    # 拼接构造Url
    url = buildUrl(req)
    # append Cookie
    addCookie(req, url)

    # open
    if browser.current_url != url:
        browser.get(url)

    # if this is post we need to post and refresh
    if not req.method:
        v = requests.post(url, data=req.convertedParams, headers=req.header,
                      timeout=timeout, verify=False, proxies=core.conf.proxies)
        browser.refresh()

    # put value
    res.content = browser.page_source
    res.check = browser.execute_script("return hacked")
    return res.content



