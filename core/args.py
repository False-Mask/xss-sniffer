import argparse

import core.conf
from core import conf, log
from core.encoders import base64
from core.log import setup_logger
from model.net import Request
from model.opt import CmdOpt
import re

logger = setup_logger(__name__)


def parse() -> CmdOpt:
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='url', dest='target')
    parser.add_argument('--data', help='post data', dest='paramData')
    parser.add_argument('-e', '--encode', help='encode payloads', dest='encode')
    parser.add_argument('--fuzzer', help='fuzzer', dest='fuzz', action='store_true')
    parser.add_argument('--update', help='update', dest='update', action='store_true')
    parser.add_argument('--timeout', help='timeout', dest='timeout', type=int, default=conf.timeout)
    parser.add_argument('--proxy', help='use prox(y|ies)', dest='proxy', action='store_true')
    parser.add_argument('--crawl', help='crawl', dest='recursive', action='store_true')
    parser.add_argument('--json', help='treat post data as json', dest='jsonData', action='store_true')
    parser.add_argument('--path', help='inject payloads in the path', dest='path', action='store_true')
    parser.add_argument('--seeds', help='load crawling seeds from a file', dest='args_seeds')
    parser.add_argument('-f', '--file', help='load payloads from a file', dest='args_file')
    parser.add_argument('-l', '--level', help='level of crawling', dest='level', type=int, default=2)
    parser.add_argument('--headers', help='add headers', dest='add_headers', nargs='?', const=True)
    parser.add_argument('-t', '--threads', help='number of threads', dest='threadCount', type=int,
                        default=conf.threadCount)
    parser.add_argument('-d', '--delay', help='delay between requests', dest='delay', type=int,
                        default=conf.delay)
    parser.add_argument('--skip', help='don\'t ask to continue', dest='skip', action='store_true')
    parser.add_argument('--skip-dom', help='skip dom checking', dest='skipDOM', action='store_true')
    parser.add_argument('--blind', help='inject blind XSS payload while crawling', dest='blindXSS', action='store_true')
    parser.add_argument('--console-log-level', help='Console logging level', dest='console_log_level',
                        default=log.console_log_level, choices=log.log_config.keys())
    parser.add_argument('--file-log-level', help='File logging level', dest='file_log_level',
                        choices=conf.log_config.keys(), default=None)
    parser.add_argument('--log-file', help='Name of the file to log', dest='log_file', default=conf.log_file)
    args = parser.parse_args()

    conf.console_log_level = args.console_log_level
    conf.file_log_level = args.file_log_level
    conf.log_file = args.log_file
    conf.globalVariables = args

    cmd = CmdOpt()
    request = Request()
    initRequest(request)
    request.convertParams()
    initCmdOpt(cmd, request)
    if not conf.globalVariables.proxy:
        conf.proxies = {}
    conf.globalVariables = vars(conf.globalVariables)
    return cmd


def initCmdOpt(cmd: CmdOpt, req: Request):
    args = conf.globalVariables
    cmd.req = req
    cmd.skip = args.skip
    cmd.skipDOM = args.skipDOM
    cmd.encoding = base64 if args.encode and args.encode == 'base64' else False

    # logs
    core.conf.console_log_level = args.console_log_level
    core.conf.file_log_level = args.file_log_level
    core.conf.log_file = args.log_file


def initRequest(request: Request):
    args = conf.globalVariables
    # make sure the http method type
    request.method = False if args.paramData else True
    # parse header
    if type(args.add_headers) is bool:
        pass
        # headers = extractHeaders(prompt())
    elif type(args.add_headers) is str:
        request.header = strToDic(args.add_headers)
    else:
        request.header = conf.headers
    # rawUrl
    request.rawUrl = conf.globalVariables.target
    # check
    if not request.rawUrl:
        logger.error("url can't be null")
        return

    split = request.rawUrl.split('?')

    # url & params
    request.url = split[0]  # url
    # pass argument for GOT and POST
    if not request.method:
        data = args.paramData
        parts = data.split('&')
        dataParams = dict()
        for part in parts:
            kv = part.split('=')
            if len(kv) < 2:
                kv.append('')
            dataParams[kv[0]] = kv[1]
        request.data = dataParams
    else:
        params = dict()
        parts = split[1].split('&')
        for part in parts:
            kv = part.split('=')
            if len(kv) < 2:
                kv.append('')
            params[kv[0]] = kv[1]
        request.params = params
    # timeout
    request.timeout = args.timeout
    # delay
    request.delay = args.delay


def strToDic(headers):
    headers = headers.replace('\\n', '\n')
    sorted_headers = {}
    matches = re.findall(r'(.*):\s(.*)', headers)
    for match in matches:
        header = match[0]
        value = match[1]
        try:
            if value[-1] == ',':
                value = value[:-1]
            sorted_headers[header] = value
        except IndexError:
            pass
    return sorted_headers
