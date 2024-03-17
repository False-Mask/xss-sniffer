import copy
from fuzzywuzzy import fuzz
import re
from urllib.parse import unquote
from model.opt import CmdOpt
from core.conf import xsschecker
from core.requester import requester
from core.utils import replaceValue, fillHoles


def checker(cmd: CmdOpt, payload, positions):
    req = cmd.req
    params = req.convertedParams
    encoding = cmd.encoding
    checkString = 'st4r7s' + payload + '3nd'
    if encoding:
        checkString = encoding(unquote(checkString))
    reqCopy = copy.deepcopy(cmd.req)
    reqCopy.convertedParams = replaceValue(params, xsschecker, checkString, copy.deepcopy)
    responseRes = requester(reqCopy)
    # selenium check通过
    if responseRes.useSelenium:
        if responseRes.check:
            return [100]
        else:
            return []
    # requester 请求
    response = responseRes.content.lower()
    reflectedPositions = []
    for match in re.finditer('st4r7s', response):
        reflectedPositions.append(match.start())
    filledPositions = fillHoles(positions, reflectedPositions)
    #  Itretating over the reflections
    num = 0
    efficiencies = []
    for position in filledPositions:
        allEfficiencies = []
        try:
            reflected = response[reflectedPositions[num]
                :reflectedPositions[num]+len(checkString)]
            efficiency = fuzz.partial_ratio(reflected, checkString.lower())
            allEfficiencies.append(efficiency)
        except IndexError:
            pass
        if position:
            reflected = response[position:position+len(checkString)]
            if encoding:
                checkString = encoding(checkString.lower())
            efficiency = fuzz.partial_ratio(reflected, checkString)
            if reflected[:-2] == ('\\%s' % checkString.replace('st4r7s', '').replace('3nd', '')):
                efficiency = 90
            allEfficiencies.append(efficiency)
            efficiencies.append(max(allEfficiencies))
        else:
            efficiencies.append(0)
        num += 1
    return list(filter(None, efficiencies))


def filterChecker(cmd: CmdOpt, occurences):
    positions = occurences.keys()
    sortedEfficiencies = {}
    # adding < > to environments anyway because they can be used in all contexts
    environments = set(['<', '>'])
    for i in range(len(positions)):
        sortedEfficiencies[i] = {}
    for i in occurences:
        occurences[i]['score'] = {}
        context = occurences[i]['context']
        if context == 'comment':
            environments.add('-->')
        elif context == 'script':
            environments.add(occurences[i]['details']['quote'])
            environments.add('</scRipT/>')
        elif context == 'attribute':
            if occurences[i]['details']['type'] == 'value':
                if occurences[i]['details']['name'] == 'srcdoc':  # srcdoc attribute accepts html data with html entity encoding
                    environments.add('&lt;')  # so let's add the html entity
                    environments.add('&gt;')  # encoded versions of < and >
            if occurences[i]['details']['quote']:
                environments.add(occurences[i]['details']['quote'])
    for environment in environments:
        if environment:
            efficiencies = checker(cmd, environment, positions)
            efficiencies.extend([0] * (len(occurences) - len(efficiencies)))
            for occurence, efficiency in zip(occurences, efficiencies):
                occurences[occurence]['score'][environment] = efficiency
    return occurences

