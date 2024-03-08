from abc import abstractmethod, ABC


class Payload:
    malicious: str
    doubleClosure: bool
    attrs: dict

    @abstractmethod
    def inject(self) -> str:
        pass

"<script>alert(1)</script>"
"<html >"
"<img src=1 onerror=alert(1) />"
'" autofocus onfocus=alert(1)'
"' autofocus onfocus=alert(1)"

"-->"
class HTMLNormalPayload(Payload, ABC):
    malicious = ''
    tag = ''

    def inject(self) -> str:
        res = ""
        if self.doubleClosure:
            begin = "<" + self.tag
            attrs = ""
            for attr in self.attrs:
                pass
                # attrs += attr[0] + "=" + attr[1] +

