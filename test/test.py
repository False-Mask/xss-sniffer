import base64

from core.generator import *

occ = dict()
occ[2794] = {
    "context": 'html',
    'detail': {},
    'position': 2794,
    'score': {
        '<': 60,
        '>': 60
    }
}
xsschecker = 'v3dm0s'

test2Str = """ <html>
    <test src="v3dm0sa "></test>>
    <ac a="v3dm0sad "></ac>>
    <r 2="v3dm0s as"></r>>
    <tester>v3dm0sa <tester/>

    <script>
    asf
        v3dm0saawfjaf
    </script>

    <style>
    12 v3dm0s12

    </style>

    </html>


    """

attr1 = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
<a href='v3dm0s'></a>
</body>
</html>
"""

if __name__ == '__main__':
    def testGene():
        l = [test2Str, attr1]
        for e in l:
            generator(getLocationInfo(e, xsschecker), e)


    def testLoc():
        for i in occ:
            element = occ[i]
            context: str = element['context']
            pos: int = element['position']
            infos = getLocationInfo(test2Str, xsschecker)
            for info in infos:
                print(info.t, info.tags)


    # testGene()
    base = base64.b64encode('hack()'.encode('utf-8'))
    print(base)
