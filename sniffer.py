from core import args
from env import checker
from core.scanner import doScan, Mode

# 打印
print(r'''
██╗  ██╗███████╗███████╗    ███████╗███╗   ██╗██╗███████╗███████╗███████╗██████╗ 
╚██╗██╔╝██╔════╝██╔════╝    ██╔════╝████╗  ██║██║██╔════╝██╔════╝██╔════╝██╔══██╗
 ╚███╔╝ ███████╗███████╗    ███████╗██╔██╗ ██║██║█████╗  █████╗  █████╗  ██████╔╝
 ██╔██╗ ╚════██║╚════██║    ╚════██║██║╚██╗██║██║██╔══╝  ██╔══╝  ██╔══╝  ██╔══██╗
██╔╝ ██╗███████║███████║    ███████║██║ ╚████║██║██║     ██║     ███████╗██║  ██║
╚═╝  ╚═╝╚══════╝╚══════╝    ╚══════╝╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝
                                                                                 
''')
# check env
checker.check()
# parse args
cmd = args.parse()

mode: Mode = Mode.NORMAL
if cmd.crawl:
    mode = Mode.CRAWL
elif cmd.fuzz:
    mode = Mode.FUZZ
elif cmd.args_seeds:
    mode = Mode.SEEDS
doScan(mode)

