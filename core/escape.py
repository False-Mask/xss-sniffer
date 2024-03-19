from core.utils import randomHtmlEntry

doubleWriteEscape = ["script"]
htmlEntryEscape = ['javascript']


def buildEscape(payloads: list[str]) -> list[str]:
    res: list[str] = []
    # script双写逃逸
    for escape in doubleWriteEscape:
        for payload in payloads:
            if payload.count('<script'):
                strLen = len(escape)
                if strLen <= 1:
                    continue
                escapeValue = escape[:(strLen // 2)] + escape + escape[(strLen // 2):]
                payload = payload.replace(f"<{escape}>", f"<{escapeValue}>")
                payload = payload.replace(f"</{escape}>", f"</{escapeValue}>")
                res.append(payload)

    # 实体字符
    for escape in htmlEntryEscape:
        for payload in payloads:
            if payload.count('javascript'):
                res.append(payload.replace(escape, randomHtmlEntry(escape)))
    return res

