import env

from env import checker
from core import args

# 打印
print("xss sniffer")
# check env
checker.check()
# 
args.parse()

