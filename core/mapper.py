from core.utils import randomUpper

attrs = ['href', 'onmouseover', 'onfocus', 'src', 'onload', 'action', 'data']


def mapPayloads(payloads: list[str]):
    res: list[str] = []
    for payload in payloads:
        res.append(mapPayload(payload))
    return res


def mapPayload(payload: str) -> str:
    # 大小写绕过
    res: str = payload
    for attr in attrs:
        res = res.replace(attr+'=', randomUpper(attr)+'=')
    return res

