
from datetime import datetime

DEBUGGING = True
# 1 = ERROR
# 2 = LOG
# 3 = DEBUG
LEVEL = 3

def error(msg):
    if DEBUGGING and LEVEL >= 1:
        print("[E] {}:{}".format(datetime.now(), msg))

def log(msg):
    if DEBUGGING and LEVEL >= 2:
        print("[L] {}:{}".format(datetime.now(), msg))

def debug(msg):
    if DEBUGGING and LEVEL >= 3:
        print("[D] {}:{}".format(datetime.now(), msg))