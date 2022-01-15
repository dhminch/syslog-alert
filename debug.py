
from datetime import datetime

class Debug:
    verbosity = 1

    def set_verbosity(level):
        Debug.verbosity = level

    def error(msg):
        if Debug.verbosity >= 1:
            print("[E] {}: {}".format(datetime.now(), msg))

    def log(msg):
        if Debug.verbosity >= 2:
            print("[L] {}: {}".format(datetime.now(), msg))

    def debug(msg):
        if Debug.verbosity >= 3:
            print("[D] {}: {}".format(datetime.now(), msg))