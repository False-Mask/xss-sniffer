from env import checker
from core import args
from core.scanner import scan

# 打印
print("xss sniffer")
# check env
checker.check()
# parse args
cmd = args.parse()
scan(cmd)

