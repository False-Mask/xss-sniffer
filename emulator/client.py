import copy
import time
import urllib.parse
from typing import Dict, Any, Type

from selenium import webdriver
from selenium.common import UnexpectedAlertPresentException, WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.remote.errorhandler import ErrorHandler, ErrorCode, ExceptionMapping
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
    if not cmd.enableUI:
        options.add_argument("--headless")

    # init browser
    global browser
    browser = webdriver.Chrome(
        options=options,
        keep_alive=True
    )

    # config
    # browser.implicitly_wait(5)
    # browser.error_handler =
    global wait
    wait = WebDriverWait(browser, 10)


def request(req: Request, res: RequestResult) -> str:
    # wait.until(expected_conditions.presence_of_element_located())
    url = req.url
    # add /
    if not url.endswith('/'):
        url += '/'
    if len(req.convertedParams) > 0 and not url.endswith('?'):
        url += '?'
    # append kv
    for (k, v) in req.convertedParams.items():
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
                try:
                    browser.add_cookie({
                        "name": keyValue[0].strip(),
                        "value": keyValue[1].strip(),
                        "domain": domain,
                    })
                except UnexpectedAlertPresentException as exp:
                    res.check = True
                    return res.content

    if browser.current_url != url:
        browser.get(url)
    try:
        res.content = browser.page_source
    except UnexpectedAlertPresentException as alertExp:
        # wait.until(EC.alert_is_present())
        # browser.switch_to.alert.accept()
        res.check = True
        res.content = browser.page_source
    except Exception as exp:
        print("Raise")
        raise exp
    return res.content




# test
if __name__ == '__main__':
    from core.args import parse



    cmd = parse()
    initClient(cmd)
    rr = RequestResult()
    print(request(cmd.req, rr))

    time.sleep(10)
    rr = RequestResult()
    print(request(cmd.req, rr))
    time.sleep(100000000000)
