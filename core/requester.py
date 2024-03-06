import random
import requests
import time
from urllib3.exceptions import ProtocolError
import warnings

import core.conf
from core.utils import converter, getVar
from core.log import setup_logger
from model.net import Request

logger = setup_logger(__name__)

warnings.filterwarnings('ignore')  # Disable SSL related warnings


def requester(request: Request):
    # if getVar('jsonData'):
    #     data = converter(data)
    # elif getVar('path'):
    #     url = converter(data, url)
    #     data = []
    #     GET, POST = True, False

    method = request.method
    delay = request.delay
    header = request.header
    url = request.url
    data = request.data
    timeout = request.timeout

    time.sleep(delay)
    user_agents = ['Mozilla/5.0 (X11; Linux i686; rv:60.0) Gecko/20100101 Firefox/60.0',
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
                   'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 OPR/43.0.2442.991']
    if 'User-Agent' not in header:
        request.header['User-Agent'] = random.choice(user_agents)
    elif header['User-Agent'] == '$':
        header['User-Agent'] = random.choice(user_agents)

    # log start ==>
    logger.debug('Requester url: {}'.format(url))
    if not method:
        logger.debug('Requester GET!')
    else:
        logger.debug('Requester POST!')
    logger.debug_json('Requester data:', data)
    logger.debug_json('Requester headers:', header)
    # log end  ==>

    if method:
        response = requests.get(url, params=data, headers=header,
                                timeout=timeout, verify=False, proxies=core.conf.proxies)
    elif getVar('jsonData'):
        response = requests.post(url, json=data, headers=header,
                                 timeout=timeout, verify=False, proxies=core.conf.proxies)
    else:
        response = requests.post(url, data=data, headers=header,
                                 timeout=timeout, verify=False, proxies=core.conf.proxies)
    return response
