import copy
from queue import Queue
from urllib.parse import urlparse, unquote, urlunparse, ParseResult, urljoin
from bs4 import BeautifulSoup, Tag, ResultSet
import requests
from requests import Response

import core
from core import conf
from core.check import filterChecker, checker
from core.colors import *
from core.conf import xsschecker, minEfficiency, timeout
from core.fuzzer import fuzzer
from core.generator import generator
from core.htmlParser import htmlParser
from core.requester import requester
from core.utils import getUrl, getParams
from core.log import setup_logger
from enum import Enum

from model.net import Request
from model.opt import CmdOpt
from . import mygenerator
import re

from .args import cmdOpt

logger = setup_logger(__name__)


class Mode(Enum):
    SINGLE_FUZZ = 1
    BRUTE_FORCER = 2
    NORMAL = 3
    SCRAWL = 4


# def scan(mode: Mode):
#     pass


# TODO
def singleFuzz(target, paramData, encoding, headers, delay, timeout):
    GET, POST = (False, True) if paramData else (True, False)
    # If the user hasn't supplied the root url with http(s), we will handle it
    if not target.startswith('http'):
        try:
            response = requester('https://' + target, {},
                                 headers, GET, delay, timeout)
            target = 'https://' + target
        except:
            target = 'http://' + target
    logger.debug('Single Fuzz target: {}'.format(target))
    host = urlparse(target).netloc  # Extracts host out of the url
    logger.debug('Single fuzz host: {}'.format(host))
    url = getUrl(target, GET)
    logger.debug('Single fuzz url: {}'.format(url))
    params = getParams(target, paramData, GET)
    logger.debug_json('Single fuzz params:', params)
    if not params:
        logger.error('No parameters to test.')
        quit()
    # WAF = wafDetector(
    #     url, {list(params.keys())[0]: xsschecker}, headers, GET, delay, timeout)
    # if WAF:
    #     logger.error('WAF detected: %s%s%s' % (green, WAF, end))
    # else:
    #     logger.good('WAF Status: %sOffline%s' % (green, end))

    for paramName in params.keys():
        logger.info('Fuzzing parameter: %s' % paramName)
        paramsCopy = copy.deepcopy(params)
        paramsCopy[paramName] = xsschecker
        fuzzer(url, paramsCopy, headers, GET,
               delay, timeout, encoding)


def findAllInputs(tag: Tag):
    if tag.name == 'input':
        return 'type' in tag.attrs and tag.attrs['type'] == 'text'
    elif tag.name in ['textarea', 'select']:
        return True
    else:
        return False


# 对给定的url解析出参数类型。
def buildRequest(req: Request, responseText: str) -> Request:
    bs = BeautifulSoup(responseText, "html.parser")
    forms = bs.find_all(name="form")
    req = copy.deepcopy(req)
    for form in forms:
        attr: dict[str, str] = form.attrs
        if 'method' in attr.keys():
            # Method
            method = attr['method']
            req.method = method.lower() == 'get'
            # Url
            if 'action' not in attr.keys() or attr['action'] in ['#', '']:
                pass
            else:
                req.rawUrl = urljoin(req.rawUrl, attr['action'])
            req.parseUrl()
            # params
            params: dict[str, str] = dict()
            for tag in form.find_all(findAllInputs):
                attr: dict[str, str] = tag.attrs
                if 'name' in attr.keys():
                    params[attr['name']] = ''
            if req.method:
                req.params = params
            else:
                req.data = params
            req.convertParams()
        else:
            return Request()
    return req


def parseUrl(req: Request) -> ParseResult:
    return urlparse(req.rawUrl)


def findUrl(tag: Tag) -> bool:
    if "href" in tag.attrs.keys():
        link = tag.attrs['href']
        if not link.startswith('#'):
            return True
    return False


def close(url):
    if url[len(url) - 1] != '/':
        return url + '/'
    return url


def getChildNodes(responseText: str, request: Request) -> list[Request]:
    bs = BeautifulSoup(responseText, "html.parser")
    childTags: ResultSet = bs.find_all(findUrl)
    res: list[Request] = []
    for i in childTags:
        if i.attrs['href'].startswith('http'):
            newReq = copy.deepcopy(request)
            newReq.rawUrl = i.attrs['href']
            newReq.parseUrl()
            res.append(newReq)
        else:
            newReq = copy.deepcopy(request)
            newReq.rawUrl = urljoin(request.url, i.attrs['href'])
            newReq.parseUrl()
            res.append(newReq)
    return res


def get(curReq: Request) -> Response:
    return requests.get(curReq.rawUrl, params=curReq.convertedParams, headers=curReq.header, timeout=timeout,
                        verify=False, proxies=core.conf.proxies)


# 过滤不必要的请求
# login关键字过滤 && 只爬取当前host的内容
def requestFilter(primary: Request, curReq: Request) -> bool:
    if len(re.findall("{host}".format(host=parseUrl(primary).netloc), curReq.rawUrl)) != 0 and len(
            re.findall("logout", curReq.rawUrl)) == 0:
        return True
    else:
        return False


def scanXssForCurNode(req, curNormalResponse: Response):
    request: Request = buildRequest(req, curNormalResponse.text)
    cmd = copy.deepcopy(cmdOpt)
    cmd.req = request
    scan(cmd)
    pass


# 广度优先遍历
def traversal(request: Request):
    visited = set()
    q = Queue()
    q.put(request)
    while q.qsize() > 0:
        curReq: Request = q.get()
        # 防止重复遍历
        item = parseUrl(curReq).path
        if item in visited or not requestFilter(request, curReq):
            continue
        print("scan for ---> {url}".format(url=curReq.rawUrl))
        # # 遍历当前节点(扫描漏洞)
        visited.add(item)
        # 先进行一次简单的请求，查看注入点 & 进行link的search
        curNormalResponse = get(curReq)
        # 为当前节点扫描XSS
        scanXssForCurNode(curReq, curNormalResponse)
        # 添加子节点
        children: list[Request] = getChildNodes(curNormalResponse.text, request)
        for child in children:
            q.put(child)


def scan(cmd: CmdOpt):
    req = cmd.req
    method = req.method
    target = req.rawUrl
    url = req.url
    params = req.convertedParams
    skipDOM = cmd.skipDOM
    encoding = cmd.encoding
    logger.debug('Scan target: {}'.format(target))
    responseRes = requester(req)
    response = responseRes.content
    skip = cmd.skip
    # dom
    if not skipDOM:
        logger.run('Checking for DOM vulnerabilities')
        highlighted = dom(response)
        if highlighted:
            logger.good('Potentially vulnerable objects found')
            logger.red_line(level='good')
            for line in highlighted:
                logger.no_format(line, level='good')
            logger.red_line(level='good')
    host = urlparse(target).netloc  # Extracts host out of the url
    # log ==> scan
    logger.debug('Host to scan: {}'.format(host))
    logger.debug('Url to scan: {}'.format(url))
    logger.debug_json('Scan parameters:', params)
    # log ==> scan

    if not params:
        logger.error('No parameters to test.')
        quit()
    for paramName in params.keys():
        cmdCopy = copy.deepcopy(cmd)
        logger.info('Testing parameter: %s' % paramName)
        if encoding:
            cmdCopy.req.convertedParams[paramName] = encoding(xsschecker)
        else:
            cmdCopy.req.convertedParams[paramName] = xsschecker

        responseRes = requester(cmdCopy.req)
        responseText = responseRes.content
        occurences = htmlParser(responseText, encoding)
        positions = occurences.keys()
        logger.debug('Scan occurences: {}'.format(occurences))
        if not occurences:
            logger.error('No reflection found')
            # continue
        else:
            logger.info('Reflections found: %i' % len(occurences))

        logger.run('Analysing reflections')
        efficiencies = filterChecker(cmdCopy, occurences)
        logger.debug('Scan efficiencies: {}'.format(efficiencies))
        logger.run('Generating payloads')
        # vectors = generator(occurences, responseText)
        vectors = mygenerator.generate(responseText)
        total = len(vectors)
        if total == 0:
            logger.error('No vectors were crafted.')
            continue
        logger.info('Payloads generated: %i' % total)
        progress = 0
        for vect in vectors:
            if conf.globalVariables['path']:
                vect = vect.replace('/', '%2F')
            loggerVector = vect
            progress += 1
            logger.run('Progress: %i/%i\r' % (progress, total))
            if not method:
                vect = unquote(vect)
            efficiencies = checker(cmdCopy, vect, positions)
            if not efficiencies:
                for i in range(len(occurences)):
                    efficiencies.append(0)
            bestEfficiency = max(efficiencies)
            if bestEfficiency == 100 or (vect[0] == '\\' and bestEfficiency >= 95):
                logger.red_line()
                logger.good('Payload: %s' % loggerVector)
                logger.info('Efficiency: %i' % bestEfficiency)
                if not skip:
                    choice = input(
                        '%s Would you like to continue scanning? [y/N] ' % que).lower()
                    if choice != 'y':
                        quit()
            elif bestEfficiency > minEfficiency:
                logger.red_line()
                logger.good('Payload: %s' % loggerVector)
                logger.info('Efficiency: %i' % bestEfficiency)
        logger.no_format('')


def dom(response):
    highlighted = []
    sources = r'''\b(?:document\.(URL|documentURI|URLUnencoded|baseURI|cookie|referrer)|location\.(href|search|hash|pathname)|window\.name|history\.(pushState|replaceState)(local|session)Storage)\b'''
    sinks = r'''\b(?:eval|evaluate|execCommand|assign|navigate|getResponseHeaderopen|showModalDialog|Function|set(Timeout|Interval|Immediate)|execScript|crypto.generateCRMFRequest|ScriptElement\.(src|text|textContent|innerText)|.*?\.onEventName|document\.(write|writeln)|.*?\.innerHTML|Range\.createContextualFragment|(document|window)\.location)\b'''
    scripts = re.findall(r'(?i)(?s)<script[^>]*>(.*?)</script>', response)
    sinkFound, sourceFound = False, False
    for script in scripts:
        script = script.split('\n')
        num = 1
        allControlledVariables = set()
        try:
            for newLine in script:
                line = newLine
                parts = line.split('var ')
                controlledVariables = set()
                if len(parts) > 1:
                    for part in parts:
                        for controlledVariable in allControlledVariables:
                            if controlledVariable in part:
                                controlledVariables.add(
                                    re.search(r'[a-zA-Z$_][a-zA-Z0-9$_]+', part).group().replace('$',  '\$'))
                pattern = re.finditer(sources, newLine)
                for grp in pattern:
                    if grp:
                        source = newLine[grp.start():grp.end()].replace(' ', '')
                        if source:
                            if len(parts) > 1:
                                for part in parts:
                                    if source in part:
                                        controlledVariables.add(
                                            re.search(r'[a-zA-Z$_][a-zA-Z0-9$_]+', part).group().replace('$', '\$'))
                            line = line.replace(source, yellow + source + end)
                for controlledVariable in controlledVariables:
                    allControlledVariables.add(controlledVariable)
                for controlledVariable in allControlledVariables:
                    matches = list(filter(None, re.findall(r'\b%s\b' % controlledVariable, line)))
                    if matches:
                        sourceFound = True
                        line = re.sub(r'\b%s\b' % controlledVariable, yellow + controlledVariable + end, line)
                pattern = re.finditer(sinks, newLine)
                for grp in pattern:
                    if grp:
                        sink = newLine[grp.start():grp.end()].replace(' ', '')
                        if sink:
                            line = line.replace(sink, red + sink + end)
                            sinkFound = True
                if line != newLine:
                    highlighted.append('%-3s %s' % (str(num), line.lstrip(' ')))
                num += 1
        except MemoryError:
            pass
    if sinkFound or sourceFound:
        return highlighted
    else:
        return []
