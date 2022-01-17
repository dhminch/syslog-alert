
from datetime import datetime

class Debug:
    verbosity = 1

    def set_verbosity(level):
        Debug.verbosity = level

    def error(msg):
        if Debug.verbosity >= 1:
            log_msg = "[E] {}: {}".format(datetime.now(), msg)
            print(log_msg)

    def log(msg):
        if Debug.verbosity >= 2:
            log_msg = "[L] {}: {}".format(datetime.now(), msg)
            print(log_msg)

    def debug(msg):
        if Debug.verbosity >= 3:
            log_msg = "[D] {}: {}".format(datetime.now(), msg)
            print(log_msg)
